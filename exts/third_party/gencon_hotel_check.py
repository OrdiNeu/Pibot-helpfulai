#!/usr/bin/env python
from __future__ import print_function

# Python System imports
import logging
from exts.utils.DiscordArgParse import DiscordArgParse, DiscordArgparseParseError
from discord.ext import commands
from argparse import Action, ArgumentTypeError, SUPPRESS
from datetime import datetime, timedelta
from json import loads as loads
from os.path import abspath, dirname, join as pathjoin
from re import compile as reCompile, IGNORECASE as RE_IGNORECASE, sub
from sys import version_info
from threading import Thread
from time import sleep

# pypi imports
from requests import get, post, HTTPError, ConnectionError, RequestException

# Version specific imports
if version_info <= (3, 5):
    from HTMLParser import HTMLParser
    from HTMLParser import unescape
else:
    from html.parser import HTMLParser
    from html import unescape

logger = None

firstDay, lastDay, startDay = datetime(2019, 7, 27), datetime(2019, 8, 6), datetime(2019, 8, 1)
lastAlerts = set()

distanceUnits = {
    1: 'blocks',
    2: 'yards',
    3: 'miles',
    4: 'meters',
    5: 'kilometers',
}


def clean_json(json_string):
    json_string = sub(r"\\\\\"", "\\\"", json_string)
    json_string = sub(r"\\\'", "\'", json_string)
    json_string = sub(r"\\x", "", json_string)
    return json_string


class PasskeyParser(HTMLParser):
    def __init__(self, resp):
        HTMLParser.__init__(self)
        self._starttag = str()
        self._collect_data = False
        self.data = None
        self.feed(resp)
        self.close()

    def handle_starttag(self, tag, attrs):
        if self.data is not None:
            return
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "application/json":
            logger.debug("Found tag '{}' under '{}' ".format(tag, attrs.get("id")))
            self._collect_data = True
        else:
            return

    def handle_endtag(self, tag):
        if self._starttag == "ul":
            self._collect_data = False
            self._starttag = ""
            logger.debug("endtag '{}'".format(tag))

    def handle_data(self, data):
        if self._collect_data:
            logger.debug("handle_data: '{}'".format(data))
            self.data = data
            self._collect_data = False


def type_day(arg):
    try:
        d = datetime.strptime(arg, '%Y-%m-%d')
    except ValueError:
        raise ArgumentTypeError("%s is not a date in the form YYYY-MM-DD" % arg)
    if not firstDay <= d <= lastDay:
        raise ArgumentTypeError("%s is outside the Gencon housing block window" % arg)
    return arg


def type_distance(arg):
    if arg == 'connected':
        return arg
    try:
        return float(arg)
    except ValueError:
        raise ArgumentTypeError("invalid float value: '%s'" % arg)


def type_regex(arg):
    try:
        return reCompile(arg, RE_IGNORECASE)
    except Exception as e:
        raise ArgumentTypeError("invalid regex '%s': %s" % (arg, e))


class EmailAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        dest = getattr(namespace, self.dest)
        if dest is None:
            dest = []
            setattr(namespace, self.dest, dest)
        dest.append(tuple(['email'] + values))


def get_options(args=None):
    parser = DiscordArgParse()
    parser.add_argument(
        '--guests', type=int, default=1,
        help='number of guests')
    parser.add_argument(
        '--children', type=int, default=0,
        help='number of children')
    parser.add_argument(
        '--rooms', type=int, default=1,
        help='number of rooms')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--checkin', type=type_day, metavar='YYYY-MM-DD', default=startDay.strftime('%Y-%m-%d'),
        help='check in')
    group.add_argument(
        '--wednesday', dest='checkin', action='store_const',
        const=(startDay - timedelta(1)).strftime('%Y-%m-%d'),
        help='check in on Wednesday')
    parser.add_argument(
        '--checkout', type=type_day, metavar='YYYY-MM-DD',
        default=(startDay + timedelta(3)).strftime('%Y-%m-%d'),
        help='check out')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--max-distance', type=type_distance, metavar='BLOCKS',
        help="max hotel distance that triggers an alert (or 'connected' to require skywalk hotels)")
    group.add_argument(
        '--connected', dest='max_distance', action='store_const', const='connected',
        help='shorthand for --max-distance connected')
    parser.add_argument(
        '--budget', type=float, metavar='PRICE', default='99999',
        help='max total rate (not counting taxes/fees) that triggers an alert')
    parser.add_argument(
        '--hotel-regex', type=type_regex, metavar='PATTERN', default=reCompile('.*'),
        help='regular expression to match hotel name against')
    parser.add_argument(
        '--room-regex', type=type_regex, metavar='PATTERN', default=reCompile('.*'),
        help='regular expression to match room against')
    parser.add_argument(
        '--show-all', action='store_true',
        help='show all rooms, even if miles away (these rooms never trigger alerts)')
    parser.add_argument(
        '--ssl-insecure', action='store_false', dest='ssl_cert_verify',
        help=SUPPRESS)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--delay', type=int, default=1, metavar='MINS',
        help='search every MINS minute(s)')
    group.add_argument(
        '--once', action='store_true',
        help='search once and exit')
    parser.add_argument(
        '--test', action='store_true', dest='test',
        help='trigger every specified alert and exit')
    group = parser.add_argument_group('required arguments')
    group.add_argument(
        '--key', required=True,
        help='key (see the README for more information)')
    group = parser.add_argument_group('alerts')
    group.add_argument(
        '--popup', dest='alerts', action='append_const', const=('popup',),
        help='show a dialog box')
    group.add_argument(
        '--cmd', dest='alerts', action='append', type=lambda arg: ('cmd', arg), metavar='CMD',
        help='run the specified command, passing each hotel name as an argument')
    group.add_argument(
        '--browser', dest='alerts', action='append_const', const=('browser',),
        help='open the Passkey website in the default browser')
    group.add_argument(
        '--email', dest='alerts', action=EmailAction, nargs=3, metavar=('HOST', 'FROM', 'TO'),
        help='send an e-mail')
    options = parser.parse_args(args)
    return options


def check_source_repo():
    # Attempt to check the version against Github, but ignore it if it fails
    # Only updating the version when a breaking bug is fixed (a crash or a failure to search correctly)
    try:
        version = open(pathjoin(dirname(abspath(__file__)), 'version')).read()
        resp = get(url='https://raw.githubusercontent.com/mrozekma/gencon-hotel-check/master/version')
        # resp = urlopen(
        #    'https://raw.githubusercontent.com/mrozekma/gencon-hotel-check/master/version', context=ssl_context)
        # if resp.getcode() == 200:
        if resp.status_code == 200:
            # head = resp.read()
            if version != resp.headers:
                logger.warning("Warning: This script is out-of-date. If you downloaded it via git, use 'git pull' to "
                               "fetch the latest version. Otherwise, visit https://github.com/mrozekma/gencon-hotel-check")

    except (RequestException, IOError) as e:
        logger.debug("Failed to check source Repo with exception '{}'".format(e))


class GenconHotel:
    """Hotel Checking related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['gencon_hotel'], pass_context=True)
    async def gencon_hotel_check(self, ctx):
        global print_function
        print_function = self.bot.say
        args = ctx.message.content.split() + "--once --show-all".split()
        if len(args) > 1:
            args = args[1:]
        else:
            args = []
        event_url = 'https://book.passkey.com/event/49822766/owner/10909638/rooms/select'
        options = get_options(args=args)
        start_url = "https://book.passkey.com/reg/%s/null/null/1/null/null" % options.key
        alert_fns = self.setup_alert_handlers(start_url, options)
        while True:
            logging.info("Starting session")
            search_resp = self.session_setup(event_url=event_url, start_url=start_url, options=options)
            if search_resp is not None:
                await self.search(search_resp=search_resp, alert_fns=alert_fns, options=options)
                if options.once:
                    return 0
            sleep(60 * options.delay)

    async def setup_alert_handlers(self, start_url, options):
        # Setup the alert handlers
        alert_fns = list()
        success = True
        for alert in options.alerts or []:
            if alert[0] == 'popup':
                try:
                    import win32api
                    alert_fns.append(
                        lambda preamble, hotels: win32api.MessageBox(0, 'Gencon Hotel Search', "%s\n\n%s" % (
                            preamble,
                            '\n'.join(
                                "%s: %s: %s" % (hotel['distance'], hotel['name'], hotel['room']) for hotel in hotels))))
                except ImportError:
                    try:
                        import Tkinter, tkMessageBox
                        def handle(preamble, hotels):
                            window = Tkinter.Tk()
                            window.wm_withdraw()
                            tkMessageBox.showinfo(title='Gencon Hotel Search',
                                                  message="%s\n\n%s" % (preamble, '\n'.join(
                                                      "%s: %s: %s" % (hotel['distance'], hotel['name'], hotel['room'])
                                                      for hotel in hotels)))
                            window.destroy()

                        alert_fns.append(handle)
                    except ImportError:
                        await self.bot.say("Unable to show a popup. Install either win32api (if on Windows) or Tkinter")
                        success = False
            elif alert[0] == 'cmd':
                import subprocess
                alert_fns.append(
                    lambda preamble, hotels, cmd=alert[1]: subprocess.Popen(
                        [cmd] + [hotel['name'] for hotel in hotels]))
            elif alert[0] == 'browser':
                import webbrowser
                alert_fns.append(lambda preamble, hotels: webbrowser.open(start_url))
            elif alert[0] == "discord_current_chat":
                await self.bot.say()
            elif alert[0] == 'email':
                from email.mime.text import MIMEText
                import getpass, smtplib, socket
                _, host, fromEmail, toEmail = alert
                password = getpass.getpass(
                    "Enter password for %s (or blank if %s requires no authentication): " % (fromEmail, host))

                def smtpConnect():
                    try:
                        smtp = smtplib.SMTP_SSL(host)
                    except socket.error:
                        smtp = smtplib.SMTP(host)
                    if password:
                        smtp.login(fromEmail, password)
                    return smtp

                try:
                    smtpConnect()

                    def handle(preamble, hotels):
                        msg = MIMEText("%s\n\n%s\n\n%s" % (preamble, '\n'.join(
                            "  * %s: %s: %s" % (
                                hotel['distance'], hotel['name'].encode('utf-8'), hotel['room'].encode('utf-8'))
                            for hotel in hotels), start_url), 'plain', 'utf-8')
                        msg['Subject'] = 'Gencon Hotel Search'
                        msg['From'] = fromEmail
                        msg['To'] = toEmail
                        smtpConnect().sendmail(fromEmail, toEmail, msg.as_string())

                    alert_fns.append(handle)
                except Exception as e:
                    await self.bot.say(e)
                    success = False
        if not success:
            exit(1)
        if not alert_fns:
            logger.warning(
                "Warning: You have no alert methods selected, so you're not going to know about a match unless you're"
                " staring at this window when it happens. See the README for more information")
        if options.test:
            logger.debug("Testing alerts one at a time...")
            preamble = 'This is a test'
            hotels = [{'name': 'Test hotel 1', 'distance': '2 blocks', 'rooms': 1, 'room': 'Queen/Queen suite'},
                      {'name': 'Test hotel 2', 'distance': '5 blocks', 'rooms': 5, 'room': 'Standard King'}]
            for fn in alert_fns:
                fn(preamble, hotels)
            logger.info("Done")
            exit(0)
        return alert_fns

    async def session_setup(self, event_url, start_url, options):
        try:
            event_url_resp = get(start_url)
        except (ConnectionError, HTTPError, RequestException) as e:
            await self.bot.say("Session request failed: %s" % e)
            return None
        if event_url_resp.status_code != 200:
            await self.bot.say("Session request failed: %d" % event_url_resp.status_code)
            return None
        if not event_url_resp.cookies:
            await self.bot.say("No session cookie received. Is your key correct?")
            return None
        logger.info("Searching... (%d %s, %d %s, %s - %s, %s)" % (
            options.guests, 'guest' if options.guests == 1 else 'guests', options.rooms,
            'room' if options.rooms == 1 else 'rooms',
            options.checkin, options.checkout,
            'connected' if options.max_distance == 'connected' else 'downtown' if options.max_distance is None else
            "within %.1f blocks" % options.max_distance))
        data = {
            'hotelId': '0',
            'blockMap.blocks[0].blockId': '0',
            'blockMap.blocks[0].checkIn': options.checkin,
            'blockMap.blocks[0].checkOut': options.checkout,
            'blockMap.blocks[0].numberOfGuests': str(options.guests),
            'blockMap.blocks[0].numberOfRooms': str(options.rooms),
            'blockMap.blocks[0].numberOfChildren': str(options.children),
        }
        try:
            search_resp = post(event_url, params=data, cookies=event_url_resp.cookies)
        except ConnectionError:
            search_resp = None
        if search_resp is None or search_resp.status_code not in (200, 302):
            await self.bot.say("Search failed: {}".format(search_resp.status_code))
            return None
        return search_resp

    async def search(self, search_resp, alert_fns, options):
        global lastAlerts
        # search_resp.html.render()
        logger.debug("Starting Parser")
        parser = PasskeyParser(str(search_resp.content))
        if not parser.data:
            await self.bot.say("Failed to find search results")
            return False
        json_string = clean_json(parser.data)
        logger.debug("cleaned json string: '{}'".format(json_string))
        hotels = loads(json_string)
        await self.bot.say("Results:   (%s)" % datetime.now())
        alerts = []
        await self.bot.say("   %-15s %-10s %-80s %s" % ('Distance', 'Price', 'Hotel', 'Room'))
        for hotel in hotels:
            for block in hotel['blocks']:
                # Don't show hotels miles away unless requested
                if hotel['distanceUnit'] == 3 and not options.show_all:
                    continue

                connected = ('Skywalk to ICC' in (hotel['messageMap'] or ''))
                simpleHotel = {
                    'name': unescape(hotel['name']),
                    'distance': 'Skywalk' if connected else "%4.1f %s" % (
                        hotel['distanceFromEvent'], distanceUnits.get(hotel['distanceUnit'], '???')),
                    'price': int(sum(inv['rate'] for inv in block['inventory'])),
                    'rooms': min(inv['available'] for inv in block['inventory']),
                    'room': unescape(block['name']),
                }
                result = "'''\n%-15s $%-9s %-80s (%d) %s\n'''" % (
                    simpleHotel['distance'], simpleHotel['price'], simpleHotel['name'], simpleHotel['rooms'],
                    simpleHotel['room'])
                # I don't think these distances (yards, meters, kilometers) actually appear in the results,
                # but if they do assume it must be close enough regardless of --max-distance
                close_enough = hotel['distanceUnit'] in (2, 4, 5) \
                               or (hotel['distanceUnit'] == 1 and (options.max_distance is None or (
                        isinstance(options.max_distance, float) and hotel[
                    'distanceFromEvent'] <= options.max_distance))) \
                               or (options.max_distance == 'connected' and connected)
                cheap_enough = simpleHotel['price'] <= options.budget
                regex_match = options.hotel_regex.search(simpleHotel['name']) and options.room_regex.search(
                    simpleHotel['room'])
                if close_enough and cheap_enough and regex_match:
                    alerts.append(simpleHotel)
                    await self.bot.say(' !'),
                else:
                    await self.bot.say('  '),
                    await self.bot.say(result)
        if alerts:
            alert_hash = {(alert['name'], alert['room']) for alert in alerts}
            if alert_hash <= lastAlerts:
                logger.info("Skipped alerts (no new rooms in nearby hotel list)")
            else:
                num_hotels = len(set(alert['name'] for alert in alerts))
                preamble = "%d %s near the ICC:" % (num_hotels, 'hotel' if num_hotels == 1 else 'hotels')
                for fn in alert_fns:
                    # Run each alert on its own thread since some (e.g. popups)
                    #  are blocking and some (e.g. e-mail) can throw
                    Thread(target=fn, args=(preamble, alerts)).start()
                logger.info("Triggered alerts")
        else:
            alert_hash = set()
        lastAlerts = alert_hash
        return True


def setup(bot):
    bot.add_cog(GenconHotel(bot))
