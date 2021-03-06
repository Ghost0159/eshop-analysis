#!/usr/bin/env python3

import os
import sys

import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import copy
import csv
from xml.etree import ElementTree
from typing import List

titlekeyurl = None 
# use shop_id=1 for urlbases to limit this to the 3DS eshop
urlbase_eshop = 'https://samurai.wup.eshop.nintendo.net/samurai/ws/{lang}/titles?shop_id=4&limit=200&offset={offs}'
urlbase_title = 'https://samurai.wup.eshop.nintendo.net/samurai/ws/{lang}/title/{eshop_id}'
urlbase_eid = 'https://ninja.ctr.shop.nintendo.net/ninja/ws/titles/id_pair?title_id[]={title_id}'
urlbase_ec = 'https://ninja.wup.shop.nintendo.net/ninja/ws/{lang}/title/{eshop_id}/ec_info?shop_id=4&lang=en'
urlbase_price = 'https://api.ec.nintendo.com/v1/price?ids={eshop_id}&country={lang}&lang=en'
urlbase_lang = 'https://samurai.wup.eshop.nintendo.net/samurai/ws/{lang}/languages'

dumpdest = 'dumped'
resultdest = 'results'

csv_eshop_analysis = resultdest + '/' + 'eshop_analysis_all_in_one.csv'
csv_3dsdb_releases = resultdest + '/' + '3dsdb_releases.csv'
csv_titlekeydb = resultdest + '/' + 'titlekeys.csv'
csv_unique_downloads = resultdest + '/' + 'unique_download_titles.csv'
csv_missing_3dsdb_from_eshop = resultdest + '/' + 'missing_3dsdb_from_eshop.csv'
csv_missing_retail_dumps_no_download = resultdest + '/' + 'missing_retail_dumps_no_download.csv'
csv_missing_downloads_only_retail = resultdest + '/' + 'missing_downloads_only_retail.csv'
csv_missing_titlekeys = resultdest + '/' + 'missing_titlekeys.csv'
csv_missing_archive_eshop = resultdest + '/' + 'missing_archive_eshop.csv'
csv_missing_archive_all = resultdest + '/' + 'missing_archive_all.csv'

csv_fieldnames_eshop = ['title_id', 'product_code', 'region_id', 'name', 'publisher', 'publisher_id', 'platform', 'platform_id', 'genre', 'size', 'release_eshop', 'release_retail', 'eshop_regions', 'score', 'votes', 'best_price', 'best_price_region', 'titlekey_known', '3dsdb_id', 'alternative_download', 'alternative_with_titlekey', 'best_alternative']
csv_fieldnames_3dsdb = ['title_id', 'product_code', 'region_id', 'name', 'publisher', 'region', 'languages', 'size', '3dsdb_id', 'alternative_download', 'alternative_with_titlekey', 'best_alternative']
csv_fieldnames_titlekeys = ['title_id', 'product_code', 'titlekey_dec', 'titlekey_enc', 'password', 'name', 'region', 'size']

langs_english = ('US', 'GB', 'CA', 'AU')
langs_main = ('US', 'GB', 'JP', 'AU', 'ES', 'DE', 'IT', 'FR', 'NL', 'CA', 'RU', 'KR', 'TW', 'HK')
langs_all = ('US', 'GB', 'JP', 'AU', 'ES', 'DE', 'IT', 'FR', 'NL', 'AX', 'AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BV', 'BR', 'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC', 'CO', 'KM', 'CD', 'CG', 'CK', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'GF', 'PF', 'TF', 'GA', 'GM', 'GE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GN', 'GW', 'GY', 'HT', 'HM', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IL', 'JM', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC', 'MN', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'AN', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU', 'RW', 'SH', 'KN', 'LC', 'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'CS', 'SC', 'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'UM', 'UY', 'UZ', 'VU', 'VA', 'VE', 'VN', 'VG', 'VI', 'WF', 'EH', 'YE', 'ZM', 'ZW')

platform_dict = {'18' : 'Nintendo 3DS Retail Only', '19' : 'Nintendo 3DS Download Only', '20' : 'Nintendo DSiWare', '21' : 'Nintendo Game Boy', '22' : 'Nintendo Game Boy Color', '23' : 'Nintendo Game Boy Advance', '24' : 'NES', '25' : 'Game Gear', '26' : 'Turbografx', '30' : 'Wii U Retail Only', '43' : 'Downloadable Video', '63' : 'Nintendo 3DS Software Update', '83' : 'Nintendo 3DS Software Update (JP)', '103' : 'Nintendo 3DS Retail/Download', '124' : 'Wii U Download Only', '125' : 'Wii U Retail/Download', '143' : 'Wii U TVii', '163' : 'NES', '164' : 'Super NES', '165' : 'Wii U Uplay', '166' : 'TurboGrafx16', '167' : 'MSX', '168' : 'Game Boy Advance', '169' : 'Nintendo DS', '170' : 'Nintendo 64', '171' : 'Wii Retail/Download', '1001' : 'New 3DS Download Only', '1002' : 'New 3DS Retail/Download', '1003' : 'New 3DS Software Update', '1004' : 'Super Nintendo'}

region_id_pref = {'A' : 0, 'P' : 1, 'E' : 2, 'J' : 3, 'S' : 4, 'D' : 5, 'F' : 6, 'I' : 7, 'H' : 8, 'R' : 9, 'W' : 10, 'K' : 11, 'V' : 12, 'X' : 13, 'Y' : 14, 'Z' : 15, 'T' : 16, 'O' : 17, 'U' : 18}

merged_eshop_elements = []
db_release_elements = []
titlekeydb_data = []


def write_eshop_content(el, out):
    # sort data
    for ee in el:
        if ee.tag != 'content':
            print(ee.tag)
            print(ee.get('id'))
    el.sort(key=lambda x: int(x.get('index')))

    # generate merged XML
    merged_root = ElementTree.Element('contents')
    merged_root.set('contents', str(len(el)))
    merged_root.extend(el)

    # save to file
    merged = ElementTree.ElementTree(merged_root)
    merged.write(out)
    

def is_eshop_available(lang):
    av = True
    
    # check availability of eshop
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    with requests.session() as s:
        s.verify = False
        url = urlbase_lang.format(lang=lang)
        with s.get(url) as r:
            el = ElementTree.fromstring(r.content)
            er = el.find('error')
            if er is not None:
                av = False
                
    return(av)


def add_eshop_ec_info():
    # certificate available
    if not os.path.isfile('ctr-common-1.crt') or not os.path.isfile('ctr-common-1.key'):
        return

    # only continue if certs are available
    with requests.session() as s:
        s.verify=False
        s.cert=('ctr-common-1.crt', 'ctr-common-1.key')
        
        count_all = len(merged_eshop_elements)
        count_ok = 0
        for cn in merged_eshop_elements:
            eid = cn.find('title').get('id')
            lng = 'US'
            er = cn.find('eshop_regions')
            for l in langs:
                if er.find(l).text == 'true':
                    lng = l
                    break

            url = urlbase_ec.format(lang=lng, eshop_id=eid)
            with s.get(url) as r:
                el = ElementTree.fromstring(r.content)
                data_root = list(el)[0]
                cn.insert(1, data_root)

            count_ok += 1
            print('Adding eshop ecommerce info: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')

        print('Adding eshop ecommerce info: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\n')
        
        
def add_eshop_prices(currency):
    # certificate available
    if not os.path.isfile('ctr-common-1.crt') or not os.path.isfile('ctr-common-1.key'):
        return
    
    print('Adding eshop prices: ...', end = '\r')

    # get exchange rates
    rates = {}
    url = 'http://www.floatrates.com/daily/{curr}.json'.format(curr=currency.lower())
    with requests.get(url) as r:
        tbl = r.json()
        for e in tbl:
            rates[e.strip().upper()] = float(tbl[e]['rate'])
    rates[currency.upper()] = float(1.00)
    
    # get eshop prices
    with requests.session() as s:
        s.verify = False
        s.cert=('ctr-common-1.crt', 'ctr-common-1.key')

        count_all = len(merged_eshop_elements)
        count_ok = 0
        for cn in merged_eshop_elements:
            eid = cn.find('title').get('id')
            er = cn.find('eshop_regions')
            p_best = 999999999.0
            p_region = 'none'
            for l in langs:
                if er.find(l).text != 'true':
                    continue
                url = urlbase_price.format(eshop_id=eid, lang=l)
                with s.get(url) as r:
                    pdata = r.json()
                    if not 'prices' in pdata or len(pdata['prices']) == 0:
                        continue
                    pd = pdata['prices'][0]
                    if not 'sales_status' in pd or pd['sales_status'] != 'onsale':
                        continue
                    if not 'regular_price' in pd:
                        continue
                    price = None
                    if 'discount_price' in pd:
                        price = pd['discount_price']
                    else:
                        price = pd['regular_price']
                    curr = price['currency']
                    if not curr in rates:
                        continue
                    p_best_this = float(price['raw_value']) / rates[curr]
                    if p_best_this < p_best:
                        p_best = p_best_this
                        p_region = l
            # add eshop_prices
            sel = ElementTree.SubElement(cn, 'eshop_best_price')
            cur = ElementTree.SubElement(sel, 'p_best')
            cur.text = str(round(p_best, 2))
            cur = ElementTree.SubElement(sel, 'p_region')
            cur.text = str(p_region)
            
            if p_region != 'none':
                count_ok += 1
            print('Adding eshop prices: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')
            
        print('Adding eshop prices: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\n')


def merge_eshop_content(cn, pc, l):
    dup = False
    tt = cn.find('title')

    for cn0 in merged_eshop_elements:
        tt0 = cn0.find('title')
        pc0 = tt0.find('product_code').text

        if pc == pc0:
            # duplicate found, merge data
            dup = True

            sel = cn0.find('eshop_regions').find(l)
            sel.text = 'true'

            if tt.find('retail_sales').text == 'true':
                tt0.find('retail_sales').text = 'true'
            if tt.find('eshop_sales').text == 'true':
                tt0.find('eshop_sales').text = 'true'
            if tt.find('demo_available').text == 'true':
                tt0.find('demo_available').text = 'true'
            if tt.find('aoc_available').text == 'true':
                tt0.find('aoc_available').text = 'true'

            rd = tt.find('release_date_on_eshop')
            rd0 = tt0.find('release_date_on_eshop')
            if rd is not None and rd0 is not None and rd0.text > rd.text:
                rd0.text = rd.text
            
            rd = tt.find('release_date_on_retail')
            rd0 = tt0.find('release_date_on_retail')
            if rd is not None and rd0 is not None and rd0.text > rd.text:
                rd0.text = rd.text

            sr = tt.find('star_rating_info')
            sr0 = tt0.find('star_rating_info')
            if sr is not None and sr0 is not None:
                vt = int(sr.find('votes').text) + int(sr0.find('votes').text)
                s1 = int(sr.find('star1').text) + int(sr0.find('star1').text)
                s2 = int(sr.find('star2').text) + int(sr0.find('star2').text)
                s3 = int(sr.find('star3').text) + int(sr0.find('star3').text)
                s4 = int(sr.find('star4').text) + int(sr0.find('star4').text)
                s5 = int(sr.find('star5').text) + int(sr0.find('star5').text)
                sc = round(((s1 * 1) + (s2 * 2) + (s3 * 3) + (s4 * 4) + (s5 * 5)) / vt, 2)

                sr0.find('votes').text = str(vt)
                sr0.find('star1').text = str(s1)
                sr0.find('star2').text = str(s2)
                sr0.find('star3').text = str(s3)
                sr0.find('star4').text = str(s4)
                sr0.find('star5').text = str(s5)
                sr0.find('score').text = str(sc)

            break

    # not duplicate - copy, create eshop_region info and add element
    if not dup:
        cncp = copy.deepcopy(cn)
        ttcp = cncp.find('title')

        # add eshop_regions
        sel = ElementTree.SubElement(cncp, 'eshop_regions')
        for lng in langs:
            cur = ElementTree.SubElement(sel, lng)
            cur.text = 'false'
            if lng == l:
                cur.text = 'true'

        # add titlekey (if available)
        sel = ElementTree.SubElement(cncp, 'dectitlekey')
        if ttcp.find('eshop_sales').text == 'true':
            for ttk in titlekeydb_data:
                sr = ttk['serial']
                if sr is None:
                    continue

                # workaround for bad product codes in titlekey db
                sr_alt = None
                if sr[3:6] == '-N-':
                    sr_alt = sr[0:3] + '-P-' + sr[6:10]
                elif sr[3:6] == '-P-':
                    sr_alt = sr[0:3] + '-N-' + sr[6:10]

                if sr == pc or sr_alt == pc:
                    sel.text = ttk['titleKey']
                    break

        # remove unneeded stuff
        sel = ttcp.find('rating_info')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('price_on_retail')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('price_on_retail_detail')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('tentative_price_on_eshop')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('banner_url')
        if sel is not None:
            ttcp.remove(sel)

        merged_eshop_elements.append(cncp)

    # true if new addition
    return not dup


def get_idlist_content(path):
    # certificate available
    if not os.path.isfile('ctr-common-1.crt') or not os.path.isfile('ctr-common-1.key'):
        return
        
    # get list of eshop ids from args
    eshop_ids = []
    
    with requests.session() as s:
        s.verify = False
        s.cert=('ctr-common-1.crt', 'ctr-common-1.key')
        
        count_ok = 0
        count_tried = 0
        with open(path, 'r') as fp:
            for ln in fp:
                tid = ln.strip().upper()
                eid = None
                if len(tid) != 16:
                    continue
                count_tried += 1
                print('Collecting eshop ids: ...', end = '\r')
                url = urlbase_eid.format(title_id=tid)
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                with s.get(url) as r:
                    el = ElementTree.fromstring(r.content)
                    if el.find('title_id_pairs') is None:
                        continue
                    tidpairs = el.find('title_id_pairs')
                    if tidpairs is None or len(list(tidpairs)) == 0:
                        continue
                    for tip in tidpairs:
                        tid_p = tip.find('title_id').text
                        if tid_p != tid:
                            continue
                        eid = tip.find('ns_uid').text
                        if eid is not None and not eid in eshop_ids:
                            count_ok += 1
                            eshop_ids.append(eid)
                            print('Collecting eshop ids: ' + tid + ' -> ' + eid, end = '\n')
                
    print('Collecting eshop ids: ' + str(count_ok) + ' / ' + str(count_tried) + ' found', end = '\n')
    if len(eshop_ids) == 0:
        return
    
    # check eshops for title IDs
    with requests.session() as s:
        s.verify = False

        for l in langs:
            print('Checking ' + l + ' eshop content: ...', end = '\r')
            count_ok = 0
            count_new = 0
            offset = 0
            title_elements = []
            
            if not is_eshop_available(l):
                print('Checking ' + l + ' eshop content: not available', end = '\n')
                continue
            
            for eid in eshop_ids:
                url = urlbase_title.format(lang=l, eshop_id=eid)
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                
                # on screen output
                print('Checking ' + l + ' eshop content: ' + str(count_ok) + ' / ' + str(offset) + ' entries (' + str(count_new) + ' new)', end = '\r')
                offset += 1
                
                # one request per title
                with s.get(url) as r:
                    el = ElementTree.fromstring(r.content)
                    if el.tag != 'eshop':
                        continue
                    el.tag = 'content'
                    el.set('index', str(offset))
                    tt = el.find('title')
                    if tt is None:
                        continue
                    pc = tt.find('product_code').text
                    title_elements.append(el)

                    # merge eshope content
                    if merge_eshop_content(el, pc, l):
                        count_new += 1
                    count_ok += 1
            
            print('Checking ' + l + ' eshop content: ' + str(count_ok) + ' / ' + str(offset) + ' entries (' + str(count_new) + ' new)', end = '\n')
            if count_ok > 0:
                # save to file
                out = dumpdest + '/contents-eshop-' + l + '.xml'
                write_eshop_content(title_elements, out)

    # save merged data to file
    add_eshop_ec_info()
    out = dumpdest + '/contents-eshop-MERGED.xml'
    write_eshop_content(merged_eshop_elements, out)
 

def get_eshop_content():
    # handle eshop content
    with requests.session() as s:
        s.verify = False

        for l in langs:
            print('Scraping ' + l + ' eshop content: ...', end = '\r')
            count_ok = 0
            count_new = 0
            offset = 0
            title_elements = []
            while True:
                url = urlbase_eshop.format(lang=l, offs=offset)
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                with s.get(url) as r:
                # with s.get(url, verify='nintendo-ca-g3.pem') as r:
                    el = ElementTree.fromstring(r.content)
                    # check this eshop
                    if el.find('contents') is None:
                        break
                    # the only element inside an eshop element should be a contents one.
                    contents_root = list(el)[0]

                    # check length
                    length = int(contents_root.get('length'))
                    if length <= 0:
                        break
                    offset += length

                    # on screen output
                    print('Scraping ' + l + ' eshop content: ' + str(count_ok) + ' / ' + str(offset) + ' entries (' + str(count_new) + ' new)', end = '\r')

                    # clean up and add elements from the contents root to the title_elements lists
                    for cn in contents_root:
                        tt = cn.find('title')
                        if tt is None:
                            continue
                        pc = tt.find('product_code').text
                        title_elements.append(cn)

                        # merge eshope content
                        if merge_eshop_content(cn, pc, l):
                            count_new += 1
                        count_ok += 1

            if offset > 0:
                print('Scraping ' + l + ' eshop content: ' + str(count_ok) + ' / ' + str(offset) + ' entries (' + str(count_new) + ' new)', end = '\n')
                # save to file
                out = dumpdest + '/contents-eshop-' + l + '.xml'
                write_eshop_content(title_elements, out)

    # save merged data to file
    add_eshop_ec_info()
    out = dumpdest + '/contents-eshop-MERGED.xml'
    write_eshop_content(merged_eshop_elements, out)


def get_3dsdb_content():
    print('Loading 3DSDB cart data: ...', end = '\r')

    url = 'http://3dsdb.com/xml.php'
    with requests.get(url) as r:
        out = dumpdest + '/3dsdb.xml'
        with open(out, 'wb') as f:
            f.write(r.content)

        el = ElementTree.fromstring(r.content)

        # count and get rid of crap (eshop, demo, update, movie, selfmade) entries
        count_all = 0
        count_ok = 0
        for rl in el:
            print('Loading 3DSDB cart data: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')

            count_all += 1
            type = rl.find('type').text
            serial = rl.find('serial').text
            code = serial[4:8]
            if not serial.startswith(('CTR-', 'KTR-')):
                continue
            if not code.startswith(('A', 'B', 'C', 'E')):
                continue
            if type != '1':
                continue

            dup = False
            for rl0 in el:
                if rl is rl0:
                    break
                elif serial == rl0.find('serial').text:
                    dup = True
                    break
            if dup:
                continue

            db_release_elements.append(rl)
            count_ok += 1

        print('Loading 3DSDB cart data: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\n')


def get_titlekeydb_data():
    global titlekeydb_data
    print('Loading titlekeydb data: ...', end = '\r')

    url = titlekeyurl + '/json'
    with requests.get(url) as r:
        out = dumpdest + '/titlekeydb.json'
        with open(out, 'wb') as f:
            f.write(r.content)
        titlekeydb_data = r.json()

        print('Loading titlekeydb data: ' + str(len(titlekeydb_data)) + ' entries', end = '\n')


def analyse_3dsdb(english_only):
    # analyse the data and build CSV files
    with open(csv_missing_3dsdb_from_eshop, 'w', encoding='utf-8') as md_csv, open(csv_3dsdb_releases, 'w', encoding='utf-8') as db_csv:

        # find cart dumps missing in eshop
        mdw = csv.DictWriter(md_csv, fieldnames = csv_fieldnames_3dsdb, lineterminator='\n')
        dbw = csv.DictWriter(db_csv, fieldnames = csv_fieldnames_3dsdb, lineterminator='\n')
        mdw.writeheader()
        dbw.writeheader()
        count_all = len(db_release_elements)
        count_missing = 0

        for rl in db_release_elements:
            print('Adding missing entries from 3dsdb.com: ' + str(count_missing) + ' / ' + str(count_all) + ' entries', end = '\r')
            serial = rl.find('serial').text
            type = serial[0:3]
            code = serial[4:8]
            gid = serial[4:7]
            rid = serial[7:8]
            pc_p = type + '-P-' + code
            pc_n = type + '-N-' + code
            eshop_alt = []
            eshop_alt_ttk = []

            if english_only and not rid in ('A', 'E', 'P'):
                continue

            found = False
            for cn in merged_eshop_elements:
                pc = cn.find('title').find('product_code').text
                es = cn.find('title').find('eshop_sales').text
                ttk = cn.find('dectitlekey').text
                if pc == pc_n or pc == pc_p:
                    found = True
                elif pc[0:3] == type and pc[6:9] == gid and es == 'true':
                    eshop_alt.append(pc)
                    if ttk is not None:
                        eshop_alt_ttk.append(pc)

            best_alt = ''
            if rid in region_id_pref:
                ba_pref = region_id_pref[rid]
                for a in eshop_alt:
                    if a[9:10] in region_id_pref:
                        ba_pref0 = region_id_pref[a[9:10]]
                        if ba_pref0 < ba_pref:
                            ba_pref = ba_pref0
                            best_alt = a

            title_id = rl.find('titleid').text
            region = rl.find('region').text
            lang = rl.find('languages').text
            name = rl.find('name').text
            pub = rl.find('publisher').text
            dbid = rl.find('id').text
            size = rl.find('trimmedsize').text

            if not found:
                mdw.writerow({'title_id': title_id, 'product_code': pc_p, 'region_id': rid, 'name': name, 'publisher': pub, 'region': region, 'languages': lang, 'size': size, '3dsdb_id': dbid, 'alternative_download': ' / '.join(eshop_alt), 'alternative_with_titlekey': ' / '.join(eshop_alt_ttk), 'best_alternative': best_alt})
                count_missing += 1
            dbw.writerow({'title_id': title_id, 'product_code': pc_p, 'region_id': rid, 'name': name, 'publisher': pub, 'region': region, 'languages': lang, 'size': size, '3dsdb_id': dbid, 'alternative_download': ' / '.join(eshop_alt), 'alternative_with_titlekey': ' / '.join(eshop_alt_ttk), 'best_alternative': best_alt})

        print('Adding missing entries from 3dsdb.com: ' + str(count_missing) + ' / ' + str(count_all) + ' entries', end = '\n')


def dump_titlekeydb():
    with open(csv_titlekeydb, 'w', encoding='utf-8') as ttk_csv:
        ttkw = csv.DictWriter(ttk_csv, fieldnames = csv_fieldnames_titlekeys, lineterminator='\n')
        ttkw.writeheader()

        count_ok = 0
        for ttk in titlekeydb_data:
            print('Dumping titlekeydb data: ' + str(count_ok) + ' entries', end = '\r')
            ttkw.writerow({'title_id': ttk['titleID'], 'product_code': ttk['serial'], 'titlekey_dec': ttk['titleKey'], 'titlekey_enc': ttk['encTitleKey'], 'password': ttk['password'], 'name': ttk['name'], 'size': ttk['size']})
            count_ok += 1
        print('Dumping titlekeydb data: ' + str(count_ok) + ' entries', end = '\n')


def build_eshop_analysis():
    with open(csv_eshop_analysis, 'w', encoding='utf-8') as ea_csv:
        eaw = csv.DictWriter(ea_csv, fieldnames = csv_fieldnames_eshop, lineterminator='\n')
        eaw.writeheader()
        count_all = len(merged_eshop_elements)
        count_ok = 0

        # process merged eshop elements
        for cn in merged_eshop_elements:
            print('Merging all entries: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')

            tt = cn.find('title')
            pl = tt.find('platform')
            pub = tt.find('publisher')
            sr = tt.find('star_rating_info')
            es = cn.find('eshop_regions')
            ec = cn.find('title_ec_info')
            ep = cn.find('eshop_best_price')

            pc = tt.find('product_code').text
            rid = pc[9:10]
            pid = pl.get('id')
            name = tt.find('name').text
            genre = tt.find('display_genre').text
            pub_name = pub.find('name').text
            pub_id = pub.get('id')
            p_best = '-'
            p_reg = '-'
            if ep is not None:
                p_best = ep.find('p_best').text
                p_reg = ep.find('p_region').text

            rel_e = ''
            if tt.find('release_date_on_eshop') is not None:
                rel_e = tt.find('release_date_on_eshop').text

            rel_r = ''
            if tt.find('release_date_on_retail') is not None:
                rel_r = tt.find('release_date_on_retail').text

            eshop_regs = []
            for l in langs:
                if es.find(l).text == 'true':
                    eshop_regs.append(l)

            score = ''
            votes = ''
            if sr is not None and sr.find('score') is not None:
                score = sr.find('score').text
                votes = sr.find('votes').text

            titlekey = cn.find('dectitlekey').text
            titlekey_known = 'false'
            if titlekey is not None and titlekey != '':
                titlekey_known = 'true'

            dbid = ''
            serial = pc[0:3] + '-' + pc[6:10]
            for rl in db_release_elements:
                if rl.find('serial').text == serial:
                    dbid = rl.find('id').text
                    break

            code = pc[6:10]
            gid = pc[6:9]
            type = pc[0:3]
            eshop_alt = []
            eshop_alt_ttk = []
            for cn0 in merged_eshop_elements:
                ttk0 = cn0.find('dectitlekey').text
                es0 = cn0.find('title').find('eshop_sales').text
                pc0 = cn0.find('title').find('product_code').text
                code0 = pc0[6:10]
                gid0 = pc0[6:9]
                type0 = pc0[0:3]
                if code0 != code and type0 == type and gid0 == gid and es0 == 'true':
                    eshop_alt.append(pc0)
                    if ttk0 is not None:
                        eshop_alt_ttk.append(pc0)

            best_alt = ''
            if rid in region_id_pref:
                ba_pref = region_id_pref[rid]
                for a in eshop_alt:
                    if a[9:10] in region_id_pref:
                        ba_pref0 = region_id_pref[a[9:10]]
                        if ba_pref0 < ba_pref:
                            ba_pref = ba_pref0
                            best_alt = a

            platform = platform_dict[pid]
            if platform is None:
                platform = ''

            title_id = ''
            size = '0'
            if ec is not None:
                title_id = ec.find('title_id').text
                if ec.find('content_size') is not None:
                    size = ec.find('content_size').text

            eaw.writerow({'title_id': title_id, 'product_code': pc, 'region_id': rid, 'name': name, 'publisher': pub_name, 'publisher_id': pub_id, 'platform': platform, 'platform_id' : pid, 'genre': genre, 'size': size, 'release_eshop': rel_e, 'release_retail': rel_r, 'eshop_regions': '/'.join(eshop_regs), 'score': score, 'votes': votes, 'best_price' : p_best, 'best_price_region' : p_reg, 'titlekey_known': titlekey_known, '3dsdb_id': dbid, 'alternative_download': ' / '.join(eshop_alt), 'alternative_with_titlekey': ' / '.join(eshop_alt_ttk), 'best_alternative': best_alt})
            count_ok += 1

        # try append data from 3DSDB
        try:
            with open(csv_missing_3dsdb_from_eshop, encoding='utf-8') as md_csv:
                mdr = csv.DictReader(md_csv)
                for r in mdr:
                    print('Merging all entries: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')
                    eaw.writerow({'title_id': r['title_id'], 'product_code': r['product_code'], 'region_id': r['region_id'], 'name': r['name'], 'publisher': r['publisher'], 'platform': platform_dict['18'], 'platform_id': '18', 'size': r['size'], 'release_retail': '3DSDB', '3dsdb_id': r['3dsdb_id'], 'alternative_download': r['alternative_download'], 'alternative_with_titlekey': r['alternative_with_titlekey'], 'best_alternative': r['best_alternative']})
                    count_ok += 1
                    count_all += 1
        except FileNotFoundError:
            pass

        print('Merging all entries: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\n')


def analyse_missing():
    with open(csv_eshop_analysis, 'r', encoding='utf-8') as ea_csv, open(csv_missing_retail_dumps_no_download, 'w', encoding='utf-8') as mrd_csv, open(csv_missing_downloads_only_retail, 'w', encoding='utf-8') as mdr_csv, open(csv_missing_titlekeys, 'w', encoding='utf-8') as mtk_csv, open(csv_missing_archive_eshop, 'w', encoding='utf-8') as mfe_csv, open(csv_missing_archive_all, 'w', encoding='utf-8') as mfa_csv, open(csv_unique_downloads, 'w', encoding='utf-8') as ud_csv:
        ear = csv.DictReader(ea_csv)
        udw = csv.DictWriter(ud_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mrdw = csv.DictWriter(mrd_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mdrw = csv.DictWriter(mdr_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mtkw = csv.DictWriter(mtk_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mfew = csv.DictWriter(mfe_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mfaw = csv.DictWriter(mfa_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        udw.writeheader()
        mrdw.writeheader()
        mdrw.writeheader()
        mtkw.writeheader()
        mfew.writeheader()
        mfaw.writeheader()

        n_unique_downloads = 0
        m_retail_dumps = 0
        m_downloads = 0
        m_downloads_alt = 0
        m_titlekey = 0
        m_archive_eshop = 0
        m_archive_all = 0
        count_all = 0

        for r in ear:
            is_unique = r['best_alternative'] is None or r['best_alternative'] == ''
            has_download = r['release_eshop'] is not None and r['release_eshop'] != ''
            has_titlekey = r['titlekey_known'] is not None and r['titlekey_known'] == 'true'
            has_cartdump = r['3dsdb_id'] is not None and r['3dsdb_id'] != ''
            has_alt = r['alternative_download'] is not None and r['alternative_download'] != ''
            has_alt_ttk = r['alternative_with_titlekey'] is not None and r['alternative_with_titlekey'] != ''

            print('Deeper analysis: ' + str(count_all) + ' entries', end = '\r')

            if has_download and is_unique:
                n_unique_downloads += 1
                udw.writerow(r)

            if not has_download and not has_cartdump:
                m_retail_dumps += 1
                mrdw.writerow(r)

            if has_download and not has_titlekey:
                m_titlekey += 1
                mtkw.writerow(r)

            if not has_download:
                m_downloads += 1

            if not has_download and not has_alt:
                m_downloads_alt += 1
                mdrw.writerow(r)

            if (not has_download or not has_titlekey) and not has_alt_ttk:
                m_archive_eshop += 1
                mfew.writerow(r)
                if not has_cartdump:
                    m_archive_all += 1
                    mfaw.writerow(r)

            count_all += 1

        print('Deeper analysis: ' + str(count_all) + ' entries', end = '\n')

        # print summary
        print('\n')
        print('Analysis summary:')
        print('--------------------------------')

        print('Total titles found             :', str(count_all))
        print('Unique download titles         :', str(n_unique_downloads))
        if titlekeyurl:
            print('Titles with missing titlekeys  :', str(m_titlekey))
        if m_downloads:
            print('Titles with no downloads       :', str(m_downloads))
            print('... and no alt downloads       :', str(m_downloads_alt))
        if m_retail_dumps:
            print('Missing cartdumps, no download :', str(m_retail_dumps))
        if titlekeyurl:
            print('No archival from eshop         :', str(m_archive_eshop))
        if m_archive_all != n_unique_downloads:
            print('No archival from eshop or 3dsdb:', str(m_archive_all))


if __name__ == '__main__':
    langs = langs_all
    english_only = False

    # say hello
    print('\n')
    print('3DS eshop analysis tool (c) 2021')
    print('--------------------------------')

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", type=str, help="specify eshop region (english/main/all/XX)")
    parser.add_argument("-l", "--list", type=str, help="specify a file with titleid list")
    parser.add_argument("-c", "--currency", type=str, help="check prices for titles, currency needs to be specified (slow)")
    if not titlekeyurl:
        parser.add_argument("-t", "--titlekeyurl", type=str, help="specify titlekey page url (with http://)")
    args = parser.parse_args()

    if args.region == 'english':
        langs = langs_english
        english_only = True
    elif args.region == 'main':
        langs = langs_main
    elif args.region == 'all':
        langs = langs_all
    elif args.region:
        langs = [ args.region ]
        english_only = True

    if not titlekeyurl and args.titlekeyurl:
        titlekeyurl = args.titlekeyurl

    # make dirs for data
    os.makedirs(dumpdest, exist_ok=True)
    os.makedirs(resultdest, exist_ok=True)

    # get all required contents
    if titlekeyurl:
        get_titlekeydb_data()
        dump_titlekeydb()
    if not args.list:
        get_3dsdb_content()
        get_eshop_content()
        analyse_3dsdb(english_only)
    else:
        get_idlist_content(args.list)
    if args.currency:
        add_eshop_prices(args.currency)
    build_eshop_analysis()
    analyse_missing()
