import urllib2
import datetime
import os
def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    before_yes = yesterday - oneday
    return yesterday, before_yes


def datetime_toString(dt):
    date =  dt.strftime("%Y-%m-%d-%H")
    date = ''.join(date.split('-')[0:-1])
    return date

if __name__ == "__main__":
    updateurl = 'http://www.polarview.aq/kml/sarfiles_update?ago=1&amp;hemi=S'
    f_xml = urllib2.urlopen(updateurl)
    data = f_xml.read()
    # update_folder = 'modisProcessing/SAR/Update/'
    update_folder = os.getcwd() + '/modisProcessing/SAR/Update/'
    # update_folder = 'C:/Users/fany/Desktop/Update/'
    today = datetime.date.today()
    today_date =  datetime_toString(today)
    today_updatesar_name = update_folder + 'sarfiles_update_' + today_date + '.xml'
    with open(today_updatesar_name, "wb") as code:
        code.write(data)
