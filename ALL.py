import csv, requests,  pathlib
# v 3.3
def writeHtml(page_name: str, csv_name: str,  html_name: str = None, sort_list: list = ['name'], int_sort = [], type_col_index: list = ['series', 'type'], include_type: set = set(), 
              exclude_type: set = set(), display_entry_name_list: list = ['name'], download_image: bool = True, force_download: bool = False) -> None: 
    '''
    page_name: name of the page
    csv_name: name of the csv file without '.csv'
    html_name: name of the html file without '.html', default csv_name
    sort_list: the order which the csv file will be sorted by column index, default sorts by first column
    int_sort: indicates which column to sort as integes
    type_col_index:
    include_type: will only add elements from the csv file to the html file if csv element column 3 or 4 is in display_type. Will add all elements if empty
    exclude_type:
    display_entry_name_list: a list of the columns the displayed name will be, a 'break' in the list will make a line break between the former and next column in the list
    download_image: bool that determins if the image probided should be download to local storage or it should use the url for the image data, default True
    force_download: bool that force the function to download the image even if download image is False and if the image is already downloaded, default False
    '''
    
    start_string = '<!DOCTYPE html>\n<html lang = "en" dir = "ltr">\n<link rel = "stylesheet" href = "../style.css">\n<head>\n\t<meta charset = "utf-8" name = "viewport" content = "width=device-width, initial-scale = 0.6">\n</head>\n\n'
    side_bar_string = '\t<script src = "../sidebar.js"></script>\n'


    if html_name == None:
        html_name = csv_name

    # replaces space with underscore for the html file
    if ' ' in html_name:
        html_name = html_name.replace(' ', '_')

    with open(csv_name + '.csv') as csv_file:
        with open('html_lists/' + html_name + '.html', 'w', encoding = 'utf-8') as html_file:

            csv_dict = csv.DictReader(csv_file, delimiter = ';')
            
            # sorts the csv file by column, order base on sort_list
            for n in sort_list:
                if n in int_sort or n == "series_number": # sort by int
                    csv_dict = sorted(csv_dict, key = lambda x: int(x[n]))
                else:
                    csv_dict = sorted(csv_dict, key = lambda x: x[n])
      

            # writes first lines of html file
            html_file.write(f'{start_string}<title>{page_name}</title>\n\n<body>\n{side_bar_string}\t<div class = "top_bar">\n\t\t<h1>{page_name}</h1>\n\t</div>\n\t<div class = "grid">\n')

            for entry in csv_dict:
                # adds more display name info from column choosen by display_row_list
                new_line = True
                displayed_name = ''
                for o in display_entry_name_list:
                    if o == 'break':
                        displayed_name += '<br>'
                        new_line = True
                    else:
                        if new_line:
                            displayed_name += entry[o]
                            new_line = False
                        else:
                            displayed_name += ' ' + entry[o]

                # finds the first index of 'vol.' in display_name, if it exist it add a line break before. made for book sites
                vol_index = displayed_name.find('vol.')
                if vol_index != -1:
                    displayed_name = displayed_name[:(vol_index - 1)] + '<br>' + displayed_name[vol_index:]

                # finds the last index of ':' in display_name, if it exist it add a line break before.
                colon_index = displayed_name.rfind(':')
                if colon_index != -1:
                    displayed_name = displayed_name[:(colon_index + 1)] + '<br>' + displayed_name[(colon_index + 2):]

                # replaces space with underscore for the html file
                sub_list_ref = entry['series']
                if ' ' in sub_list_ref:
                    sub_list_ref = sub_list_ref.replace(' ', '_')

                # image stuff
                if download_image or force_download:
                    img_path = entry['name']
                    # replaces space with underscore in the image name
                    if ' ' in img_path:
                        img_path = img_path.replace(' ', '_')
                    
                    # removes all intances from element of remove_str_list from imag_path
                    remove_str_list = ['<br>', ':', '?', ',', '!', "'", '.', '-']
                    for string in remove_str_list:
                        if string in img_path:
                            img_path = img_path.replace(string, '') 

                    img_path = 'list_img/' + img_path + '_'+ entry["type"] +'.jpg' 

                    # checks if the image is already downloaded, if not downloads it
                    if  not pathlib.Path(img_path).is_file() or force_download:
                        img_data = requests.get(entry['image']).content
                        with open(img_path, 'wb') as handler:
                            handler.write(img_data)
                    img_path = "../" + img_path
                else:
                    img_path = entry['image']


                # check if the entry shall be included or exluded
                type_set = set(entry[i] for i in type_col_index)
                include_interection_len = len(include_type.intersection(type_set))
                exclude_interection_len = len(exclude_type.intersection(type_set))


                # writing each object from the csv to the html
                if (include_interection_len != 0 or len(include_type) == 0) and (exclude_interection_len  == 0): # only write cell if type indicated
                    html_file.write(f'\t\t<div class = "grid_entry">\n\t\t\t<a href = "{sub_list_ref}.html">\n\t\t\t\t<img src = "{img_path}">\n\t\t\t</a>\n\t\t\t<br>\n\t\t\t<a class = "entry_name">\n\t\t\t\t{displayed_name}\n\t\t\t</a>\n\t\t</div>\n')

            # ends html file        
            html_file.write('\t</div>\n</body>')

            print(page_name)


def getSeriesType(csv_name: str, col_index: int) -> set:
    '''
    csv_name:
    col_index:
    '''
    with open(csv_name + '.csv') as csv_file:
        csv_dict = csv.DictReader(csv_file, delimiter = ';')
        attribute_set = set()
        non_unique_set = set()

        for entry in csv_dict:
            if entry[col_index] in attribute_set:
                non_unique_set.add(entry[col_index])
            attribute_set.add(entry[col_index])

    return [attribute_set, non_unique_set]


# # Boardgames
csv_file = 'boardgame'

# # makes main boardgame html file
writeHtml('Brætspil', csv_file)

# # makes a html file for only base games
writeHtml('Grund Spil', csv_file, html_name = 'base', include_type = {'base'})

# makes a html file for each boardgame series
boargame_series = getSeriesType(csv_file, 'series')[0]
for series in boargame_series:
    writeHtml(series, csv_file, html_name = series, include_type = {series})


# Books
csv_file = 'books'

# # make main book html file
writeHtml('Bøger', csv_file, sort_list = ['series_number', 'series', 'last_name'], display_entry_name_list = ['name', 'break', 'first_name', 'last_name'], exclude_type = {'Math'})

# makes html file for each type of book
book_type = getSeriesType(csv_file, 'type')[0]
for series in book_type:
    writeHtml(series, csv_file, html_name = series, sort_list = ['series_number', 'series', 'last_name'], display_entry_name_list = ['name', 'break', 'first_name', 'last_name'], include_type = {series})

# makes html file for each book series
book_series = getSeriesType(csv_file, 'series')[0]
for series in book_series:
    writeHtml(series, csv_file, html_name = series, sort_list = ['series_number', 'series', 'last_name'], display_entry_name_list = ['name', 'break', 'first_name', 'last_name'], include_type = {series})


# Switch games
csv_file = 'switch'

# make main switch game html
writeHtml('Switch Spil', csv_file)

# make a html for each switch series
switch_series = getSeriesType(csv_file, 'series')[0]
for series in switch_series:
    writeHtml(series, csv_file, html_name = series, include_type = {series})


# LEGO
csv_file = 'lego'

# makes main html file for LEGO
writeHtml('LEGO', csv_file, display_entry_name_list = ['name', 'break', 'number'])

# makes a html file for each LEGO series
lego_series = getSeriesType(csv_file, 'series')[0]
for series in lego_series:
    writeHtml(series, csv_file, html_name = series, display_entry_name_list = ['name', 'break', 'number'], include_type = {series})