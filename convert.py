import re
import sys


tokens = []


def parse(data):
  _init(data)
  lua_obj = {}
  _parse(0, lua_obj)
  return lua_obj


def _init(data):
  global tokens
  tokens = []
  is_string = False
  for t in re.split('([{},"])',re.sub('[ \r\n]', '', data)):
    if not t:
      continue
    if t == '"':
      is_string = not is_string
      _append_str(t)
    elif is_string:
      _append_str(t)
    elif t == '{' or t == '}':
      if not tokens or tokens[-1]:
        tokens.append(t)
      else:
        tokens[-1] = t
    elif t == ',':
      tokens.append('')
    else:
      _append_str(t)


def _append_str(s):
  global tokens
  if not tokens or tokens[-1] == '{' or tokens[-1] == '}':
    tokens.append(s)
  else:
    tokens[-1] += s


def _parse(index, fields):
  default_key = 1
  while index < len(tokens) and tokens[index] != '}':
    if tokens[index] == '{':
      fields[default_key] = {}
      index = _parse(index+1, fields[default_key])
      default_key += 1
    else:
      field = tokens[index].split('=')
      if len(field) == 1:
        fields[default_key] = field[0]
        default_key += 1
      else:
        key = field[0]
        if re.match('\[\d+\]', key):
          key = int(key[1:-1])
        if field[1]:
          fields[key] = field[1]
        else:
          fields[key] = {}
          index = _parse(index+2, fields[key])
    index += 1
  return index


def to_string(parsed_data, indent=0, obj_name=''):
  if not isinstance(parsed_data, dict):
    return parsed_data
  str_keys = [k for k in parsed_data if not isinstance(k, int)]
  int_keys = [k for k in parsed_data if isinstance(k, int)]
  fields = [('%s=' % k, to_string(parsed_data[k], indent=indent+2, obj_name=k)) for k in sorted(str_keys)]
  if obj_name in ['tCircles', 'tCountdown', 'col'] or indent == 4:
    fields.extend(
        [('', to_string(parsed_data[k], indent=indent+2, obj_name=k)) for k in sorted(int_keys)])
  else:
    fields.extend(
        [('[%d]=' % k, to_string(parsed_data[k], indent=indent+2, obj_name=k)) for k in sorted(int_keys)])
  if indent >= 6:
    pre = ''
    newline = ''
  else:
    pre = ' ' * (indent + 2)
    newline = '\r\n'
  join_str = ',' + newline
  content = join_str.join(['%s%s%s' % (pre, v[0], v[1]) for v in fields])
  if not content:
    return '{}'
  if pre:
    pre = pre[0:-2]
  return '{'+ newline + content + newline + pre + '}'


def merge_root(r_1, r_2):
  for key in r_2:
    if key not in r_1:
      r_1[key] = r_2[key]
    else:
      merge_section(r_1[key], r_2[key])


def merge_section(s_1, s_2):
  for key in s_2:
    if key not in s_1:
      s_1[key] = s_2[key]
    else:
      l = len(s_1[key])
      for k, v in s_2[key].iteritems():
        s_1[key][k+l] = v


FILES = ['base','25p-80','10p-90','5p-95']


if sys.argv[1] == 'all':
  all_obj = {1:{}}
  for f_name in FILES:
    with open('data/%s.jx3dat' % f_name, 'r') as f:
      data_string = f.read().decode('gbk')
    obj = parse(data_string)
    merge_root(all_obj[1], obj[1])
    result = to_string(obj[1], 0)
    with open('data/%s.jx3dat' % f_name, 'w+') as f:
      f.write(result.encode('gbk'))
  result = to_string(all_obj[1], 0)
  with open('data/all.jx3dat', 'w+') as f:
    f.write(result.encode('gbk'))

else:
  with open(sys.argv[1], 'r') as f:
    data_string = f.read().decode('gbk')
  obj = parse(data_string)
  result = to_string(obj[1], 0)
  with open(sys.argv[2], 'w+') as f:
    f.write(result.encode('gbk'))
