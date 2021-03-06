from scrounger.core.module import BaseModule

# helper functions
from scrounger.utils.general import pretty_grep, pretty_grep_to_str
from scrounger.utils.android import smali_dirs, track_variable
from scrounger.utils.config import Log

class Module(BaseModule):
    meta = {
        "author": "RDC",
        "description": "Checks if the application's webviews enable javascript",
        "certainty": 100
    }

    options = [
        {
            "name": "decompiled_apk",
            "description": "local folder containing the decompiled apk file",
            "required": True,
            "default": None
        },
        {
            "name": "ignore",
            "description": "paths to ignore, seperated by ;",
            "required": False,
            "default": "/com/google/;/android/support/"
        }
    ]

    regex = r"setJavaScriptEnabled"

    def run(self):
        result = {
            "title": "Application's WebViews Enable JavaScript",
            "details": "",
            "severity": "Medium",
            "report": False
        }

        # preparing variable to run
        filenames = {}
        ignore = [filepath.strip() for filepath in self.ignore.split(";")]

        Log.info("Identifying smali directories")
        dirs = smali_dirs(self.decompiled_apk)

        Log.info("Analysing application's smali code")
        for directory in dirs:
            smali = "{}/{}".format(self.decompiled_apk, directory)
            filenames.update(pretty_grep(self.regex, smali))

        report = {}
        # check var setting
        for file_name in filenames:
            report[file_name] = []

            for instance in filenames[file_name]:
                var_name = instance["details"].split(
                    "}", 1)[0].split(",", 1)[-1].strip()

                var_setting = track_variable(
                    var_name, instance["line"], file_name)

                for setting_line in var_setting:
                    if "0x1" in setting_line["details"]:
                        report[file_name] += var_setting

        for file_name in report:
            filenames[file_name] += report[file_name]

        if filenames:
            result.update({
                "report": True,
                "details": pretty_grep_to_str(
                    filenames, self.decompiled_apk, ignore)
            })

        return {
            "{}_result".format(self.name()): result
        }

