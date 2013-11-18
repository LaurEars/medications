import unittest
import meds


class TestMeds(unittest.TestCase):
    def test_image_url(self):
        url = meds.get_image_url('123','small')
        self.assertEqual('http://pillbox.nlm.nih.gov/assets/small/123.jpg',url)
        url = meds.get_image_url('123','large')
        self.assertEqual('http://pillbox.nlm.nih.gov/assets/large/123.jpg',url)

    def test_text_code(self):
        settings_filename = '.settings'
        cursor, db = meds.set_up_db(settings_filename)
        text, code = meds.generate_lut(cursor)
        self.assertEqual('Round',text['C48348'])
        self.assertEqual('C48348',code['Round'])
        cursor.close()
        db.close()