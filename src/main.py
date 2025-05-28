from webScraping import init_browser, extract_informacion, insert_auto, insert_data, get_aseguradoras

driver=init_browser("")
insert_auto(driver, 2015, "AVEO LS A STD 1.6L 4CIL 4PTAS")
insert_data(driver, "Hombre", "16072002", "Emilio", "52977", "foyagev912@ofular.com", "524385654784")
aseguradoras=get_aseguradoras(driver)
id_data, data=extract_informacion(driver, aseguradoras)
print(data)