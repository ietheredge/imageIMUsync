import argparse
import os


class App():

    def __init__(self):
        pass

    def checkds(self, thresh):
        stats = os.statvfs('/')
        avail = stats.f_bavail * stats.f_frsize
        total = stats.f_blocks * stats.f_frsize
        used = (stats.f_blocks - stats.f_bfree) * stats.f_frsize
        if avail <= thresh:
            App.compressdir(self)
            return avail, used, total
        else:
            return avail, used, total

    def compressdir(self):
        import zipfile
        zf = zipfile.ZipFile('tmp/data.zip', "w", zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk('data'):
            zf.write(root)
            for file in files:
                zf.write(os.path.join(root,file))
        zf.close()

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-ct", "--critthresh", help="critical threshold in MBs")
    args = vars(ap.parse_args())

    chkdsk = App()
    availds = chkdsk.checkds(args["critthresh"])
