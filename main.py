import argparse
import images_action


class InputParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='Save and load docker images')
        self.setup_parse()

    def setup_parse(self):
        sub_parser = self.parser.add_subparsers()

        self.parser_save = sub_parser.add_parser("save", aliases=['s'],
                                                 help="Save all images")
        self.parser_load = sub_parser.add_parser("load", aliases=['l'],
                                                 help="load all images")
        self.parser_save.set_defaults(func=self.save_fun)
        self.parser_load.set_defaults(func=self.load_fun)

    def save_fun(self,args):
        images_action.Images().save_images()
    def load_fun(self,args):
        images_action.Images().load_images()

    def parser_init(self):
        args = self.parser.parse_args()
        args.func(args)


if __name__ == "__main__":
    InputParser().parser_init()
