# 1) На вход подается пул из кадастровых номеров участков.
# Кадастровые номера взять самостоятельно любые из любого источника.
# 2) По кадастровому номеру необходимо получить координаты участка.
# 3) Из полученных координат необходимо используя яндекс карты отрисовать полигон на карте и сохранить его как картинку ( изображение со спутника)

from bs4 import BeautifulSoup as BS
import requests
import re
import os


api_key = "869e12e5-d411-496a-a608-83d56d8857b4"

# считывание файла с кадастровыми номерами
file = open("Kadastrs" + ".txt", 'r')
read_file = file.read()  # Считывание файла
file.close()
# пул из кадастровых номеров участков
kad_numbers = re.findall(r'\d+:\d+:\d+:\d+', read_file)

# определение директории и создание папки для полученных снимков
directory = os.path.dirname(os.path.abspath('Test_sberbank.py'))
cmd_mkdir_photos = 'mkdir ' + directory + '\\Photos\\'
os.system(cmd_mkdir_photos)

mas_places = []
# перебор кадастровых номеров
for kadastr in kad_numbers:
	# изменение кадастрового номера под запрос
	kadastr_edit = kadastr.replace(":", "%3A")
	kadastr_name = kadastr.replace(":", "-")
	# формирование запроса на получение адреса по кадастровому номеру
	getting_adress_uml = "https://domokod.ru/services/?cadnum=%s&searched_request_info=%s" % (kadastr_edit, kadastr_edit)
	html = requests.get(getting_adress_uml)
	soup = BS(html.content, "html.parser")
	# поиск и получение адреса и масштаба участка по кадастровому номеру
	for el in soup.select('.content-container'):
		adress_get = el.select('ul > li > span')
		adress = (str(adress_get).split("span"))
		adress_itog = adress[3][1:-2]
	area = adress[7][1:-5].replace(",", ".")
	adress_edit = adress_itog.replace(" ", "+")

	# формирование запроса на получение координат по адресу
	getting_coord_uml = "https://geocode-maps.yandex.ru/1.x/?apikey=%s&geocode=%s" % (api_key, adress_edit)
	answer_coord_xml = requests.get(getting_coord_uml).text
	#print(answer_coord_xml)

	coordinates = {"Adress":adress_itog, "Kadastr":kadastr,"Area": area, "LowerCorner":"", "UpperCorner":"", "Pos":""}
	# координаты левого нижнего угла участка
	coordinates["LowerCorner"] = answer_coord_xml[answer_coord_xml.find('lowerCorner>')+12:answer_coord_xml.find('</lowerCorner>')].replace(" ", ",")
	# координаты правого верхнего угла участка
	coordinates["UpperCorner"] = answer_coord_xml[answer_coord_xml.find('upperCorner>')+12:answer_coord_xml.find('</upperCorner>')].replace(" ", ",")
	# координаты центра участка
	coordinates["Pos"] = answer_coord_xml[answer_coord_xml.find('pos>')+4:answer_coord_xml.find('/pos>')-1].replace(" ", ",")
	mas_places.append(coordinates)
	#print(coordinates)

	# разбиение координат на долготу и широту
	longitude_center, latitude_center = coordinates["Pos"].split(",")
	longitude_bottom, latitude_bottom = coordinates["LowerCorner"].split(",")
	longitude_upper, latitude_upper = coordinates["UpperCorner"].split(",")

	# координаты углов прямоугольника
	upper_left = longitude_upper + "," + latitude_bottom
	upper_right = longitude_upper + "," + latitude_upper
	bottom_left = longitude_bottom + "," + latitude_bottom
	bottom_right = longitude_bottom + "," + latitude_upper

	# координаты углов уменьшенного прямоугольника (для более точного отображения)
	multiplier = 1.0
	if float(area) <=4000:
		multiplier = 5.0
		spn = "0.0008,0.0008"
	if float(area) >4000 and float(area) <= 7000:
		multiplier = 4.0
		spn = "0.0008,0.0008"
	if float(area) >7000 and float(area) <= 13000:
		multiplier = 3.5
		spn = "0.0013,0.0013"
	if float(area) >12000 and float(area) <= 23000:
		multiplier = 2.0
		spn = "0.002,0.002"
	upper_right_2 = str(float(longitude_center) + (abs(float(longitude_upper) - float(longitude_center))/multiplier)) + "," + str(float(latitude_center) + (abs(float(latitude_upper) - float(latitude_center))/multiplier))
	upper_left_2 = str(float(longitude_center) - (abs(float(longitude_upper) - float(longitude_center))/multiplier)) + "," + str(float(latitude_center) + (abs(float(latitude_upper) - float(latitude_center))/multiplier))
	bottom_right_2 = str(float(longitude_center) + (abs(float(longitude_upper) - float(longitude_center))/multiplier)) + "," + str(float(latitude_center) - (abs(float(latitude_upper) - float(latitude_center))/multiplier))
	bottom_left_2 = str(float(longitude_center) - (abs(float(longitude_upper) - float(longitude_center))/multiplier)) + "," + str(float(latitude_center) - (abs(float(latitude_upper) - float(latitude_center))/multiplier))

	#формирование запроса на получение снимка со спутника и отрисовки полигона по координатам (яндекс карты)
	getting_photo_uml = "https://static-maps.yandex.ru/1.x/?l=sat&ll=%s&pt=%s,pm2rdm&spn=%s&pl=c:FF0000FF,w:3,%s,%s,%s,%s,%s" % (coordinates["Pos"], coordinates["Pos"], spn, upper_left_2, upper_right_2, bottom_right_2, bottom_left_2, upper_left_2)
	#print(getting_photo_uml)
	get_photo = requests.get(getting_photo_uml)
	#print(get_photo)

	# сохранение полученного снимка картинкой
	file = directory + '\\Photos\\' + kadastr_name + ".jpg"
	out = open(file, "wb")
	out.write(get_photo.content)
	out.close()