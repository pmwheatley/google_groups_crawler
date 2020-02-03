import os
import subprocess


class GoogleGroupsCrawlerEmailPipeline(object):
    def process_item(self, item, spider):
        path, filename = os.path.split(item['path'])
        os.makedirs(path, exist_ok=True)

        with open(item['path'], "w") as fp:
            fp.write(item['email'].as_string())

        return item


class GoogleGroupsCrawlerMboxPipeline(object):
    def process_item(self, item, spider):
        subprocess.run(f"/usr/bin/formail -a 'Date:' -a 'From ' -z < {item['path']} >> {item['group']}.mbox", shell=True)
        return item
