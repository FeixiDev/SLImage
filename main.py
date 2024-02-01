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
        self.parser_save.add_argument('-f', dest='tar_name', metavar='<tar name>', help="Specify the <tar name>")
        self.parser_save.add_argument('-n', dest='name', metavar='<name>', help="point <name>")
        self.parser_load = sub_parser.add_parser("load", aliases=['l'],
                                                 help="load all images")
        self.parser_save.set_defaults(func=self.save_fun)
        self.parser_load.set_defaults(func=self.load_fun)

    def save_fun(self, args):
        # Normal save logic
        if args.tar_name is None:
            images_action.Images().save_images()
        # Save as tar logic
        else:
            images_action.Images().save_as_tar(args.tar_name, args.name)

    def load_fun(self, args):
        pass  # Implement your load functionality here

    def parser_init(self):
        args = self.parser.parse_args()
        args.func(args)


if __name__ == "__main__":
    InputParser().parser_init()
