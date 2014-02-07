import sqlite3 as sql
from collections import Counter
import urllib2

'''
Fields present:
  `SETID` varchar(64) NOT NULL DEFAULT '',
  `author_type` varchar(32) DEFAULT NULL,
  `FILE_NAME` varchar(64) DEFAULT NULL,
  `LABEL_EFFECTIVE_TIME` varchar(16) DEFAULT NULL,
  `PRODUCT_CODE` varchar(16) NOT NULL DEFAULT '',
  `NDC9` varchar(9) DEFAULT NULL,
  `PART_NUM` smallint(6) DEFAULT NULL,
  `MEDICINE_NAME` varchar(255) DEFAULT NULL,
  `PART_MEDICINE_NAME` varchar(255) DEFAULT NULL,
  `author` varchar(128) DEFAULT NULL,
  `SPLIMPRINT` varchar(64) DEFAULT NULL,
  `SPLCOLOR` varchar(32) DEFAULT NULL,
  `SPLSCORE` int(2) DEFAULT NULL,
  `SPLSHAPE` varchar(16) DEFAULT NULL,
  `SPLSIZE` decimal(7,2) DEFAULT NULL,
  `DEA_SCHEDULE_CODE` varchar(32) DEFAULT NULL,
  `SPL_INACTIVE_ING` longtext,
  `NO_RXCUI` int(1) DEFAULT NULL,
  `RXCUI` varchar(255) DEFAULT NULL,
  `RXTTY` varchar(8) DEFAULT NULL,
  `RXSTRING` varchar(512) DEFAULT NULL,
  `image_id` varchar(255) DEFAULT NULL,
  `HAS_IMAGE` int(1) DEFAULT NULL,
  `INGREDIENTS` varchar(2048) DEFAULT NULL,
  `FROM_SIS` int(1) DEFAULT NULL,
  `SPL_INGREDIENTS` varchar(2048) DEFAULT NULL,
  `PROD_MEDICINES_PRIKEY` int(10) unsigned DEFAULT NULL,
  `DOSAGE_FORM` varchar(10) DEFAULT NULL,
  `SPL_STRENGTH` varchar(2048) DEFAULT NULL,
  `RXNORM_SOURCE` varchar(10) DEFAULT NULL,
  `SPL_ID` int(8) NOT NULL DEFAULT '0',
  `source` varchar(20) DEFAULT NULL,
  `document_type` varchar(64) DEFAULT NULL,
  `ACTIVE_MOEITY` varchar(1024) DEFAULT NULL,
  `MARKETING_ACT_CODE` varchar(16) DEFAULT NULL,
  `APPROVAL_CODE` varchar(16) DEFAULT NULL,
  `IMAGE_SOURCE` varchar(10) DEFAULT NULL

DEA_SCHEDULE_CODE       DEA_schedule
color_number    color   SPL_code        hex_value
shape_number    shape_type      SPL_code
'''

# constants
name = {'color': 'color', 'shape': 'shape_type', 'dea': 'DEA_schedule'}
table_name = {'color': 'SPLCOLOR', 'shape': 'SPLSHAPE', 'dea': 'DEA_SCHEDULE_CODE'}
table = {'master': 'pillbox_master', 'color': 'SPL_color_lookup', 'shape': 'SPL_shape_lookup', 'dea': 'SPL_DEA_lookup'}


def set_up_db(settings_filename):
    """
    Performs initial setup of database, returning a cursor for executing queries
    @param settings_filename: string of filename containing sqlite3 settings
    @return: sqlite3 cursor
    """
    db = sql.connect('med.db')
    cur = db.cursor()
    return db, cur


def generate_lut(cursor):
    """
    Associate text with SPL codes
    @param cursor: sqlite3 cursor
    @return: text dict / code dict
    """
    select_color = "SELECT color, SPL_code FROM " + table['color']
    select_shape = "SELECT shape_type, SPL_code FROM " + table['shape']
    select_dea = "SELECT DEA_schedule, DEA_SCHEDULE_CODE FROM " + table['dea']
    text = {}
    code = {}

    # get colors
    cursor.execute(select_color)
    for row in cursor.fetchall():
        text[row[1]] = row[0]
        code[row[0]] = row[1]
    # get shapes
    cursor.execute(select_shape)
    for row in cursor.fetchall():
        text[row[1]] = row[0]
        code[row[0]] = row[1]
    # get DEA codes
    cursor.execute(select_dea)
    for row in cursor.fetchall():
        text[row[1]] = row[0]
        code[row[0]] = row[1]
    return text, code


def get_image_url(image_id, size='small'):
    '''
    Returns image url
    defaults to small image size
    @param image_id: SPL image_id string
    @param size: 'small' or 'large'
    '''
    image_url = 'http://pillbox.nlm.nih.gov/assets/%s/%s.jpg' % (size, image_id,)
    return image_url


# print colors/shapes/dea
def print_colors(cur):
    select_color = "SELECT * FROM " + table['color']
    cur.execute(select_color)
    print "-" * 30
    print "Colors"
    print "-" * 30
    for row in cur.fetchall():
        print row


def print_shapes(cur):
    print "-" * 30
    print "Shapes"
    print "-" * 30
    select_shape = "SELECT * FROM " + table['shape']
    cur.execute(select_shape)
    for row in cur.fetchall():
        print row


def print_dea(cur):
    print "-" * 30
    print "DEA"
    print "-" * 30
    cur.execute("SELECT * FROM " + table['dea'])
    for row in cur.fetchall():
        print row


def bad_replacement_string(query_string, replacement_items):
    '''
    Formats queries for mysql
    The escape sequence for mysqldb doesn't seem to work properly so i'll use this right now
    @param query_string: String with %s for replacements
    @param replacement_items: Items to be substituted into query_string
    @return:MySQL query string
    '''
    query = query_string % replacement_items
    return query


def translate_code(code):
    '''
    Translates SPL code to description text (e.g."C48336" means "Capsule")
    Multiple inputs and returns separated with ';'

    @param code: code for color/shape/dea_schedule
    '''
    decoded_items = []
    for item in code.split(';'):
        try:
            decoded_items.append(text[code])
        except KeyError:
            decoded_items.append(item)
    return ';'.join(decoded_items)


if __name__ == '__main__':
    settings_filename = '.settings'
    db, cur = set_up_db(settings_filename)
    text, code = generate_lut(cur)
    search_string = "SELECT %s FROM pillbox_master WHERE %s='%s' and %s='%s'"
    search_tuple = (
        'MEDICINE_NAME', table_name['color'], code['Green'], table_name['shape'], code['Pentagon (5 sides)'],)
    print "All medicines that are green and have 5 sides"
    cur.execute(bad_replacement_string(search_string, search_tuple))
    for row in cur.fetchall():
        print row

    search_string = "SELECT %s , %s, %s FROM pillbox_master WHERE %s='%s' and %s='%s'"
    search_tuple = ('MEDICINE_NAME', 'HAS_IMAGE', 'image_id', table_name['color'], code['Green'], table_name['shape'],
                    code['Pentagon (5 sides)'],)
    cur.execute(bad_replacement_string(search_string, search_tuple))
    for item in cur.fetchall():
        if item[1]:
            image_id = item[2]
            try:
                image_url = get_image_url(image_id, 'small')
                req = urllib2.Request(image_url)
                response = urllib2.urlopen(req)
                with open(image_id + '.jpg', 'wb') as output_file:
                    output_file.write(response.read())
            except urllib2.HTTPError, e:
                if e.code == 404:
                    print "HTTP 404 Error for image %s" % image_id
                else:
                    raise
            except Exception:
                print "Error: could not download file from %s" % image_url

    print '\n' + '*' * 30 + '\n'

    print "Most common color/shape combinations"
    # try counting different types of pills
    search_string = "SELECT %s, %s FROM pillbox_master"
    search_tuple = (table_name['color'], table_name['shape'],)
    cur.execute(bad_replacement_string(search_string, search_tuple))
    count = Counter()
    for row in cur.fetchall():
        count[tuple(row)] += 1
    for item, count in count.most_common():
        if count < 20:
            break
        decoded_items = []
        for color_shape in item:
            decoded_items.append(translate_code(color_shape))
        print count, decoded_items
    cur.close()
    db.close()