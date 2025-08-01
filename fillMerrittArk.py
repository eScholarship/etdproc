import sys
import consts

print("start")

def fillArk(pid, ark):
    # make sure ark follows the pattern
    if not ark.startswith('ark:/'):
        print("Invalid ark")
        return

    # if not isinstance(pid, int):
    #     print("Invalid package id")
    #     return

    print(f'filling {ark} as merrittark for package id {pid}')

    # check current queue status of the item. It should be 'merritt'
    queuename = consts.db.getQueueStatus(pid)
    if queuename != "merritt":
        print(f"Invalid queue state. Expected merritt, actual {queuename}")
        return

    # fill in merrittark in compattrs
    consts.db.saveMerrittArk(pid, ark)

    # advance queue status
    consts.db.saveQueueStatus(pid, "gw")

# Make sure args are provided
if len(sys.argv) < 3:
  sys.stderr.write("Usage: %s packageId merrittark\n" % sys.argv[0])
  sys.stderr.write("... where package id is the Id of item in packages table and ark is full Merritt ark\n")
  sys.exit(1)

packageId = sys.argv[1]
merrittArk = sys.argv[2]


fillArk(packageId, merrittArk)

print("end")