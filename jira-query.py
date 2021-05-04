import argparse
import random
import sys
import cmd2
import textwrap
import tempfile
import os
from os.path import join
import subprocess
import pprint
import yaml
from jira import JIRA


def print_text_with_prefix(space, start_prefix, cont_prefix, text):

    max_width = 200 

    if space:
        print("")

    for line in text.splitlines():
        if (len(line) > max_width):
            pos = 0
            end = len(line)
            rem = end - pos
            width = 0
            prefix = 0
            while(rem):

                if (rem < max_width):
                    width = rem
                else:
                    width = max_width

                if (pos == 0):
                    prefix = start_prefix
                else:
                    prefix = cont_prefix

                print ("{}{}".format(prefix, line[pos:pos+width]))

                pos = pos + width
                rem = rem - width
                    

        else:
            print ("{}{}".format(start_prefix, line))



def print_issue(issue, style):

    if style == "summary" or style == "all":
        print_text_with_prefix(True, 'Issue: ', '       ', issue.key + ' ' + issue.fields.summary)

    if style == "description" or style == "all":
        print_text_with_prefix(True, '>  ', '>  ', issue.fields.description)

    if style == "comments" or style == "all":
        for c in issue.fields.comment.comments:
            print(c.body)
            print_text_with_prefix(True, '>> ', '>> ', '{displayname}\n{body}'.format(displayname=c.author.displayName, body=c.body))

    if style == "attachments" or style == "all":
        for attachment in issue.fields.attachment:
            print("Name: '{filename}', size: {size}".format(filename=attachment.filename, size=attachment.size))


class CmdLineApp(cmd2.Cmd):
    """ Example cmd2 application. """

    def __init__(self):
        self.maxrepeats = 3
        delattr(cmd2.Cmd, 'do_macro')
        delattr(cmd2.Cmd, 'do_edit')
        delattr(cmd2.Cmd, 'do_py')
        delattr(cmd2.Cmd, 'do_alias')
        delattr(cmd2.Cmd, 'do_run_pyscript')
        delattr(cmd2.Cmd, 'do_run_script')

        shortcuts = dict() # cmd2.DEFAULT_SHORTCUTS
        # shortcuts.update({'h': 'history'})
        # shortcuts.update({'s': 'summary'})
        # shortcuts.update({'p': 'print'})
        # shortcuts.update({'d': 'dump'})
        # shortcuts.update({'&': 'do_attachment'})

        hfile = join(os.environ.get("APPDATA"),'JiraQuery','history')

        # Set use_ipython to True to enable the "ipy" command which embeds and interactive IPython shell
        super().__init__(use_ipython=False, multiline_commands=['orate'], shortcuts=shortcuts, persistent_history_file=hfile)
        

    id_parser = argparse.ArgumentParser()
    id_parser.add_argument('id', nargs='+', help='Bug Id(s)')

    filter_parser = argparse.ArgumentParser()
    filter_parser.add_argument('id', nargs='*', help='Filter Id(s)')

    @cmd2.with_argparser(id_parser)
    def do_summary(self, args):
        """Print oneline summary"""

        for key in args.id:
            issue = jira.issue(key)
            print_issue(issue, 'summary')

    @cmd2.with_argparser(id_parser)
    def do_print(self, args):
        """Print Bug Info"""

        for key in args.id:
            issue = jira.issue(key)
            print_issue(issue, 'all')
            

    @cmd2.with_argparser(id_parser)
    def do_open(self, args):
        """Open to Bug URL"""

        for key in args.id:
            string = 'start {}/browse/'.format(auth['server']) + key
            print(string)
            os.system(string)


    @cmd2.with_argparser(id_parser)
    def do_dump(self, args):
        """Dump Bug Info"""

        for key in args.id:
            issue = jira.issue(key)
            pprint.pprint(issue.__dict__)

    @cmd2.with_argparser(filter_parser)
    def do_filter(self, args):
        """Print Saved Filters or Specified Filter"""

        if args.id:
            for s in args.id:
                f = jira.filter(s)
                pprint.pprint(f)
                for i in jira.search_issues('filter={}'.format(s)):
                    print(i.key, i.fields.summary)

                # for c in issue.fields.comment.comments:
                #     print('>> ---- ')
                #     print('>> ', c.displayName, c.emailAddress)
                #     print('>> ', c.body)
        else:
            filters = jira.favourite_filters()
            # pprint.pprint(filters)
            for f in filters:
                print(' ', f.id, '-', f.name)

    @cmd2.with_argparser(id_parser)
    def do_attachment(self, args):
        """Print bugs in specified filter"""

        for key in args.id:
            issue = jira.issue(key)
            print_issue(issue, "summary")

            d = join(tempfile.gettempdir(), key + '.' + str(random.uniform(0,9999999)))
            os.mkdir(d)
            print("Created temp", d)
            for attachment in issue.fields.attachment:    
                f = open(join(d, attachment.filename), 'wb')
                print("Created temp", f.name)
                f.write(attachment.get()) 

            os.system("start {}".format(d))

if __name__ == '__main__':

     
    stream = open(join(sys.path[0],'jira-auth.yaml'), 'r')
    auth = yaml.safe_load(stream)
    #pprint.pprint(auth)

    jira = JIRA({'server': auth['server']}, basic_auth = (auth['user'], auth['apikey']) )
    app = CmdLineApp()
    sys.exit(app.cmdloop())
