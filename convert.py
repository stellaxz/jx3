import re
import sys


def indent(data):
  result = ['']
  lines = re.split('([{},])',data)
  pre = ''
  for l in lines:
    if l == '{':
      if len(pre) == 6 and len(result[-1]) > 0 and (
          result[-1][-1] == '{' or result[-1][-1] == ','):
        result.append(pre + l)
      else:
        result[-1] = result[-1] + l
      pre = pre + '  '
    elif l == '}':
      pre = pre[:-2]
      if len(pre) > 4:
        result[-1] = result[-1] + l
      else:
        result.append(pre + l)
    elif l == ',':
      result[-1] = result[-1] + l
    elif l:
      if len(pre) > 6:
        result[-1] = result[-1] + l
      else:
        result.append(pre + l)
  return '\r\n'.join(result)
    


with open(sys.argv[1], 'r') as f:
  data_string = f.read().decode('gbk')

result = indent(data_string)

with open(sys.argv[2], 'w+') as f:
  f.write(result.encode('gbk'))
