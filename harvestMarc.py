import consts

consts.harvestPrefix = 'marc21'
consts.harvestSet = 'UCETDs'
consts.from_date = '2025-09-01'

class harvertMarc:
    _listparams = {'metadataPrefix' : consts.harvestPrefix,
              'set': consts.harvestSet,
              'from': '2025-09-15'}
      def __init__(self):
          print("starting")