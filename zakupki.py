# !/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime

class Robot(object):
    msgs = []
    cookies = {}
    cookie_name = None
    timeout = 10

    def log(self, text):
        self.msgs.append(text)

    def request(self, url, data=None, cookies=None, headers=None, is_xml=False, is_post=False, is_bs=True):

        if not cookies:
            cookies = self.cookies

        result = False
        retry_counter = 0
        r = None

        while not result and retry_counter < 5:
            try:
                if is_post:
                    r = requests.post(url, data=data, timeout=(self.timeout + retry_counter * self.timeout),
                                      cookies=cookies, headers=headers)
                else:
                    r = requests.get(url, timeout=(self.timeout + retry_counter * self.timeout), params=data,
                                     cookies=cookies, headers=headers)
                if self.cookie_name and self.cookie_name in r.cookies:
                    self.cookies[self.cookie_name] = r.cookies[self.cookie_name]

                self.log("Requesting data from {0}...".format(url))
                result = True
            except requests.exceptions.ReadTimeout:
                print('Request timeout. Retrying...')
                retry_counter += 1
            except requests.exceptions.ConnectionError:
                print('HTTP Error. Retrying...')
                retry_counter += 1
            except:
                print('Unknown error. Retrying...')
                retry_counter += 1

        if r and r.status_code == requests.codes.ok:

            if is_xml:
                return unicode(r.text)
            else:
                if not is_bs:
                    return r.text
                else:
                    return BeautifulSoup(
                        r.text.replace("<?xml version='1.0' encoding='UTF-8'?>", '').replace('<![CDATA[', ''))

        elif r:
            print 'Error', unicode(r.text)
            self.log('ERROR: {0} {1}'.format(url, data))
            return False
        else:
            print 'Unknown Error'
            self.log('ERROR: {0} {1}'.format(url, data))
            return False

    def run(self):
        print('End')


class TenderRobot(Robot):

    url = 'http://zakupki.gov.kg/popp/view/order/list.xhtml'
    cookie_name = 'JSESSIONID'
    timeout = 60
    cookies = {}

    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'Keep-Alive',
        'Referer': 'http://zakupki.gov.kg/popp/view/order/list.xhtml',
        'X-XSS-Protection': '1; mode=block'
    }

    errors = []
    url_changed = False
    view_state = None

    def run(self):

        page = 0
        items = [{}]

        while len(items) > 0 and page < 10000:
            if page == 0:
                data = None
                headers = self.headers

            else:

                headers = {
                    'Accept': 'application/xml, text/xml, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6,es;q=0.4',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Faces-Request': 'partial/ajax',
                    'Host': 'zakupki.gov.kg',
                    'Origin': 'http://zakupki.gov.kg',
                    'Referer': 'http://zakupki.gov.kg/popp/view/order/list.xhtml',
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
                    'X-Requested-With': 'XMLHttpRequest'
                }

                data = {
                    'javax.faces.partial.ajax': 'true',
                    'javax.faces.source': 'j_idt105:j_idt106:table',
                    'javax.faces.partial.execute': 'j_idt105:j_idt106:table',
                    'javax.faces.partial.render': 'j_idt105:j_idt106:table',
                    'javax.faces.behavior.event': 'page',
                    'javax.faces.partial.event': 'page',
                    'j_idt105:j_idt106:table_pagination': 'true',
                    'j_idt105:j_idt106:table_first': page*50-40,
                    'j_idt105:j_idt106:table_rows': 50,
                    'j_idt105:j_idt106:table_encodeFeature': 'true',
                    'j_idt105': 'j_idt105',
                    'j_idt105:j_idt106:table_selection': '',
                    'j_idt105:j_idt106': 0,
                    'javax.faces.ViewState': self.view_state
                }

            if page > 0 and not self.url_changed:
                self.url = 'http://zakupki.gov.kg'+r.find('form', id='form')['action']
                self.url_changed = True

            r = self.request(self.url, data=data, headers=headers, cookies={'zakupki_locale': 'ru', 'JSESSIONID': 'EOtf1VtUtrb9_5TPLhYoues5Uo4t81odOHaEsuyQ.msc01-popp01:main-popp'}, is_post=True)

            items = self.parse_response(r if self.view_state else r.find('tbody', id='j_idt105:j_idt106:table_data'))

            if page == 0:

                if r.find('input', id='j_id1:javax.faces.ViewState:4'):
                    self.view_state = r.find('input', id='j_id1:javax.faces.ViewState:4')['value']
                # page = 280

            else:
                if r.find('update', id='j_id1:javax.faces.ViewState:4'):
                    self.view_state = r.find('update', id='j_id1:javax.faces.ViewState:4').text.replace(']]>', '')

            for i in items:

                # Get Tender details
                self.parse_tender_details(i['eid'])

                # Output to consoloe
                print i['beneficiary'].encode('utf-8'), i['published_at'], i['purpose'].encode('utf-8')

               
            page += 1

        # Outputs list of items with errors to be processed in self.parse_errors below
        print self.errors


    def parse_errors(self):

        errors = [] # put here content of self.errors from above

        self.view_state = '-8034339380070507934:-3299445731099444222'
        self.cookies = {
            'JSESSIONID': 'EOtf1VtUtrb9_5TPLhYoues5Uo4t81odOHaEsuyQ.msc01-popp01:main-popp'
        }
        for i in errors:
            r = self.get_company_profile(i)
            try:
                self.parse_company_profile(r)
            except:
                print 'Error', i

    def parse_response(self, html):

        items = []

        for tr in html.find_all('tr'):
            c = 0
            item = {'eid': tr['data-rk']}
            for td in tr.find_all('td'):
                txt = td.text.strip()
                if 0 == c:
                    item['efid'] = txt
                elif 1 == c:
                    item['beneficiary'] = txt
                elif 2 == c:
                    item['type'] = txt
                elif 3 == c:
                    item['purpose'] = txt
                elif 4 == c:
                    item['method'] = txt
                elif 5 == c:
                    item['price_planned'] = td.contents[0].replace(u"\xa0", '').replace(',', '.') if len(td.contents) else 0
                elif 6 == c:
                    item['published_at'] = datetime.datetime.strptime(txt, "%d.%m.%Y %H:%M")
                elif 7 == c:
                    item['closes_at'] = datetime.datetime.strptime(txt, "%d.%m.%Y %H:%M")
                c += 1

            items.append(item)

        return items

    def parse_tender_details(self, eid):

        r = self.request('http://zakupki.gov.kg/popp/view/order/view.xhtml?id='+str(eid), headers=self.headers)


        table = r.find('tbody', id='j_idt68:lotsTable_data')
        if not table:
            table = r.find('tbody', id='j_idt68:lotsTable2_data')

        total = 0

        if not table:
            return

        for tr in table.find_all('tr'):

            tds = tr.find_all('td')
            
            if len(tds) > 2:
                
                price = float(tds[2].text.replace(u'\xa0', '').replace(',', '.').replace(' ', ''))
                total += price

                print '-- Tender Lot', tds[1].text.strip(), price


tndr = TenderRobot()
tndr.run()