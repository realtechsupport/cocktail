# openeo_quality_check.py
# Dec 2024, RTS

def recompile(metadata):
  recompiled_metadata = {}
  for k in metadata['assets'].keys():
    recompiled_metadata[k] = {i['name']:i['statistics']['valid_percent'] for i in metadata['assets'][k]['raster:bands']}
  return recompiled_metadata


def filter(lists,threshold=96.5):
  res = []
  for k,stats in lists.items():
    if min(stats.values()) > threshold:
      res.append(k)
  return res