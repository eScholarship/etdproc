import sys

print("start")


# Make sure args are provided
if len(sys.argv) < 3:
  sys.stderr.write("Usage: %s packageId merrittark\n" % sys.argv[0])
  sys.stderr.write("... where zipname is the name of zip file from PQ without .zip extension.\n")
  sys.exit(1)

packageId = sys.argv[1]
merrittArk = sys.argv[2]
print(f'fill in Merritt ark {merrittArk} for {packageId}')

# make sure the zipname is not yet present in packages DB

#

print("end")