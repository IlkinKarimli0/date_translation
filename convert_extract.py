from difflib import get_close_matches
import re
from stem_app import *
import dateparser

MONTHS = ['yanvar','fevral','mart','aprel','may','iyun','iyul','avqust','sentyabr','oktyabr','noyabr','dekabr']

add_without_stem = [',','.',':','/','"',"'"]

eliminate_list = ["0",'in']

numbers = {'sifir':0,'bir':1,'iki':2,'üç':3,'üc':3,'uc':3,'uç':3,'üş':3,'uch':3,'dörd':4,'dört':4,'dord':4,'dort':4,'beş':5,'bes':5,'besin':5,
           'altı':6,'alti':6,'yeddi':7,'yedti':7,'yetti':7,'yedi':7,'yeti':7,'sekkiz':8,'sekgiz':8,'seggiz':8,'sekiz':8,'segiz':8,'sekkizinci':8,
           'səkkiz':8,'səkgiz':8,'səggiz':8,'səkiz':8,'səgiz':8,'doqquz':9,'doqkuz':9,'dokkuz':9,'doquz':9,'dokuz':9,
           'on':10,'iyirmi':20,'yirmi':20,'otuz':30,'otus':30,'qırx':40,'qirx':40,'əlli':50,'elli':50,'əli':50,'eli':50,
           'altmış':60,'altmis':60,'altmiş':60,'altımış':60,'altimis':60,'altimish':60,'yetmiş':70,'yetmish':70,'yetmis':70,
           'səksən':80,'səhsən':80,'səysən':80,'səgsən':80,'həşdat':80,'həşdad':80,'həştat':80,
           'seksen':80,'sehsen':80,'seysen':80,'segsen':80,'hesdat':80,'hesdad':80,'hestat':80,'heshdat':80,'heshdad':80,'heshtat':80,
           'doxsan':90,'dogsan':90,'doğsan':90,'yüz':100,'yuz':100,'yeddiyuz':700,'sekkizuz':800,'doqquzuz':900,
           'min':1000,'ikimin':2000}


suffix_shorten_dict  = {'inci':'ci','ıncı':'ci','üncü':'cu',"uncu":"cu",
                        'nci':'ci','ncı':'ci','ncü':'cu',"ncu":"cu"}



def format_suffix(suffix:str,suffix_shorten_dict:dict) -> str:
    """ We want to shorten some suffixs.
        Example: we get suffix "inci" from word "birinci" 
        Converting those suffixs as "birinci" -> "inci" -> "ci" to get "1 ci" after conversion.

        param: suffix -> which is equal to ( word - stemmed_word  -> birinci - bir => inci )
        param: suffix_shorte_dict -> dict where keys are long possible versions of the suffixes and values are shortened versions.
                                     example: {"inci":"ci"}

        return: shorten form of the input suffix
    """

    close_match = get_close_matches(   
                                       suffix, 
                                       list(  suffix_shorten_dict.keys()  ),
                                       cutoff=0.7
                                       )
    
    #check whether we found close match for suffix or not
    if close_match:
        suffix = suffix_shorten_dict[ close_match[0]  ]
    

    return suffix

def split_input(input_text:str,suffix_shortener_dict:dict) -> list:
    """ We want to seperate input to the list of elements. As well as seperate 
    the shorten form of the suffix from the list and add as an new element to the list.
    Abovementioned seperation is for conversion function later. 
    
    Such that, 
        
        "iki minin beshi" will be converted into "2000 in 5 i" and because of the suffix in 
        between 2000 and 5 mergin wont happen. 
        
        In opposite, 
        iki min besh, will be converted in to "2005"

    param : input_text is lower cased input text
    param: suffix_shorte_dict -> dict where keys are long possible versions of the suffixes and values are shortened versions.
                                    example: {"inci":"ci"}

    return: seperated form of the input list in the form of the list 
    """

    # Lower all the input so that we can understand uppercased input as well
    input_text = input_text.lower()

    # Using regex to seperate words and numbers in the input text
    #* Such that, 1992, 06, 25 should turn to the -> ['1992', ','  ,  '06' , ','  , '25']
    elems = re.findall(r'\b\w+\b|[^\w\s]', input_text) 

    #creating new elements list for handling exceptional cases by looping over previous list
    new_elems_ls = []

    for elem in elems:

        # if element in the seperated elements list is in the numbers dictionary keys add it to the new list
        # numbers dictionary is list of numbers we understand and we dont want to change them cos of we already know it is meaning
        if elem in list(numbers.keys()):
            new_elems_ls.append(elem)

        else:
            
            # Some elements we dont want to stem cos when we stem them they just disappear
            # We stored those chars in the add_without_stem list the reason to do so, when we detect problems with the 
            # stemming cases that it takes root of the word as a suffix we can add those words to the add_without_list so they

            if elem in add_without_stem:
                new_elems_ls.append(elem)
            
            #if element is in the list that we want to eliminate as an element we continue to the next iteration of the for loop
            elif elem in eliminate_list:
                continue
            
            #If those statements arent true we want to stem the word. Then add root and the shorten form of the suffix to the new_elems_ls
            else:
                
                new_elems_ls += get_root_and_suffix(elem,suffix_shortener_dict)
                

    return new_elems_ls

def get_root_and_suffix(elem:str,suffix_shortener_dict:dict) -> list:
    """This function will get seperated element from the input text and stem it.
    if it finds some suffix, it formats to the shorten form of the suffix and add it to the output list as well 
    
    param: element -> seperated element from input list. 
    param: suffix_shorte_dict -> dict where keys are long possible versions of the suffixes and values are shortened versions.
                                    example: {"inci":"ci"}

    return: list of [ root of the word, shorten suffix from the word ( if exist ) ]

    """

    root_suffix_ls = list()

    # to_stem function from stem_app returns seperated and stemmed words list from input. We give one element and expecting list with one element
    stemmed_elem = to_stem(elem)
    # if we have something in the list and given word is not eliminated totally
    if stemmed_elem:
        #take stemmed element
        stemmed_elem = stemmed_elem[0]
        #append to the abovemetioned new list
        root_suffix_ls.append(stemmed_elem)
    # if we deleted some suffix from the word element we want to extract shorten form of this suffix
    if len(elem) != len(stemmed_elem):
        suffix =  elem[-(len(elem) - len(stemmed_elem)):]
        # shorten suffix if shorten form do exist
        suffix = format_suffix(suffix,suffix_shortener_dict)
        # Add formated suffix to the list 
        root_suffix_ls.append(suffix)

    return root_suffix_ls

print('Test split input, input_text is "iki min ikinci ilin 1992, 25 on uch"',split_input('iki min ikinci ilin 1992, 25 on uch',suffix_shorten_dict))


def is_three_numerical(seperated_input_list:list) -> bool:
    """Check whether there are three OR MORE digits in the converted input list.
    Converted list example -> "iki min birinci il on besh aprel" will convert into ['2001','ci','il','15','aprel'].
    And this function will check whether in the abovementioned converted list whether there are three number or not.
    Reason behind it after we convert the splitted input list extract_entities function will try to extract numbers and months and three 
    digit in the list will be reason for error in the gotten entities so we want to detect dates with neural machine translation in this case.

    param: seperated_input_list -> list that contain elements of the input text

    return type: Boolean
    return: False if there is not three numerical value ,     example => ['1992','ci','ilin','17','aprel','i']
    return: True if there is three numerical value OR MORE    example => ['1992',':','06',':','17']    
    """

    #add numericals in to the new list, Maybe we could need this list in future for improvements so we can return it as well in future
    nums = [elem for elem in seperated_input_list if elem.isnumeric()]

    # if length of numerical values list is equal or higher than 3 we will return true 
    if      len(nums) >= 3:       return True
    else:                         return False

print("Test is three numerical: input list ['1992','17','alma','yemek'], output: ",is_three_numerical(['1992','17','alma','yemek']))   


def convert_to_ints(splitted_input_ls:list)->tuple:
    """
    Convert text written numbers to the numerical texts.
    Example: ["min","doqquz","yuz","on","besh"] -> ["1000","9","100","10","5"]
    
    param: splitted_input_ls -> splitted version of the input text with split_input function

    return: same list as input list where numbers in the text format converted into numerical string element 
            AND map of the whether some element was number that has been written in the form of text or not. Will be used for merging further
    """
    print(splitted_input_ls)
    #converted version will store here
    new_ls = []

    # for the elements text number like "bir","iki" we add 1 here if it in the another format add 0
    # it will help us not merging text numbers with numbers that's been written with digits : Case-> iki min on 5 aprel 
    map_numbers_texts = [] 

    #loop over splitted_input_ls
    for elem in splitted_input_ls:
        # Get whether element is close to some of the keys by "cutoff" percentages in the numbers dictionary
        close_matches = get_close_matches(      elem,
                                                list(numbers.keys()),
                                                cutoff = 0.81, n=1)
        
        # if we found close match we want to append to the new list
        if close_matches:               
            new_ls.append(  str(  numbers[close_matches[0]]  )  )    
            map_numbers_texts.append(1)

        # otherwise just add element so we can procced the logic further to merge numbers
        else:                           
            new_ls.append( str(elem) )
            map_numbers_texts.append(0)
            

    print(new_ls)
    return new_ls,map_numbers_texts

print(f'Test convert_to_ints function input is: ["min","doqquz","yuz","on","besh"] output: {convert_to_ints(["min","doqquz","yuz","on","besh"])}')

def handle_3_figure_numbers(converted_list:list,map_numbers_text:list) -> tuple:
    """ During conversion process we get corrosponding numbers from text example -> ["min", "uch", "yuz", "besh"] -> ["1000","3","100","5"]
        This function gets initial stage converted list and return it with merging three digit numbers,

        Such that, 

        Example input: ["1000","3","100","5"] -> output: ["1000","300","5"]

        param: converted_list initial stage converted list -> example ["1000","3","100","5"]
        param: map of the whether some element was number that has been written in the form of text or not: 
        we get this map from convert_to_int function but we need to modify it here as well

        returns: same list with handling 3 figure numbers
    """
    #new list that will contain three figures numbers in the merged form 
    new_ls = []
    #new map list cos we potentially connect two numbers and we should do same in the map list as well for not screwing out the conversion
    new_map_numbers_list = []

    # loop over initial stage converted list
    for i,(elem,mask) in enumerate(zip(converted_list,map_numbers_text)):

        # if we are not in the first element , and element is 100 we can possibly merge it with previous elem
        if elem == '100' and i != 0:

            # check whether previous element in the list is one figure number
            if len(converted_list[i-1]) == 1:
                #if it is merge them and add to the new list
                new_ls[i-1] = (  
                                str(  
                                        int(elem)*int(converted_list[i-1])
                              ))
                new_map_numbers_list[i-1] = mask
                
            else: # that mean we are in the first element of the list 
                new_ls.append(elem)# first element could be some other number as well 
                new_map_numbers_list.append(mask)

        else:
            # there is nothing to merge 
            new_ls.append(elem)
            new_map_numbers_list.append(mask)
    return new_ls,new_map_numbers_list


print(f'Test handle_3_figure_numbers function input is: ["1000","3","100","5"] output: {handle_3_figure_numbers(["1000","3","100","5"],[0,0,0,0])}')


def merge_two_num(num1:str,num2:str) -> str:
    """Merging two numbers based on their length 10,5 will be merged like 15 but 2 1000 will be merged as 2000
        param: num1 and num2 are two numbers that will be merged

        return: merged version of the num1 and num2 as an string
    """
    number_str = str()

    # if previous length of the previous num is larger than curren number example num1 = 1000 num2 = 900 summirize them
    if len(num1) > len(num2) :
        number_str = str(int(num1)+int(num2))
    # if length of the current number is larger than previous number example num1 = 2 num2 = 1000 multiply them it is only about 4 figures and 1 figure
    elif len(num1) < len(num2) and len(num2)>= 3:
        number_str = str(int(num1)*int(num2))
    # otherwise return empty string we cannot merge those numbers
    else:
        number_str = ''
    
    return number_str


def to_convert(splitted_input_ls:list)->list:
    """
    This function appears to be designed to handle numbers in a list that are expressed 
    as strings and merge them together based on certain rules. It does this by first converting
    the strings to integers and then processing them one at a time to determine whether 
    they should be merged with the previous number or not.

    param: splitted_input_ls -> splitted_version of the input text to the list

    return: converted version of the list where text numbers converted to the numerical text
    """

    #preprocess the splitted input text
    converted_ls,map_number_texts = convert_to_ints(splitted_input_ls)
    converted_ls,map_number_texts = handle_3_figure_numbers(converted_ls,map_number_texts)
    print(map_number_texts)
    print(converted_ls)
    #final converted version of the intially coverted list
    new_converted_ls = []
    #where final found numbers will store
    founded_nums = []
    #where we will store all the numbers we find while linearly searching through converted input list
    all_nums = []
    #store last founded num
    found_num = ''
    #set a mode within function that TODO
    mode = 'safe'

    #loop through converted input list 
    for i,elem in enumerate(converted_ls):

        # if element is numerical check further 
        if elem.isnumeric():
            
            # if we have found new number previous iteration or we are strating to the search now we want to add
            # current numerical elem to the <all_nums> and <found> variables to facilitate process further 
            # so, we will not need smart merge for now 

            if found_num != '' and all_nums: 
                # The part below called SMART_MERGE


                # cases like ['2000','3','10','5'] where found num is 2003 and we are lookin 10 elem now and 
                # last element of the all_nums list is 3 which is smaller than 10 in length 
                if len(found_num) > len(elem) and len(all_nums[-1]) < len(elem):

                    #this statement means we have finished reading previous number 

                    #We finished reading previous number, adding it to the founded_nums list
                    founded_nums.append(found_num)
                    # Add num to the final list
                    new_converted_ls.append(found_num)

                    #Now last founded num is element itself previous number is verrified that is it 
                    found_num = elem
                    all_nums.append(elem)

                    #enable confuse mode so that in the further iterations number wont be added to the nums as an found_num inside 
                    #else statement below
                    mode = 'confuse'

                # check if last found_num which potentially merged and created and last extracted num from converted list are not same size 
                # with the numerical elem that we are dealing with now. We cannot merge 80 with 10 or 85 with 3 
                if len(all_nums[-1]) != len(elem) and len(found_num) != len(elem) and map_number_texts[i] == map_number_texts[i-1] == 1:
                    #last gotten number coming from this merge 
                    found_num = merge_two_num(found_num,elem)
                    # and elem to the all_nums
                    all_nums.append(elem)

                # we have ready written number or we have found and potentially merged total number previous iteration so now we are looking to the new number
                else:
                    
                    #reset all_nums we found previous num we dont need parts of it 
                    all_nums = []

                    #if we are in the confusion mode we should not number that found until previous iteration such that we have added it above
                    if found_num != '' and mode == 'safe':
                        founded_nums.append(found_num)
                        new_converted_ls.append(found_num)
                    
                    #conver mode to the safe mode again 
                    mode = 'safe'
                    #we have found num replace it current element that we are handling 
                    found_num = elem
                    # maybe this element is just one part of the total number so add it to the cleaned all_nums list
                    all_nums.append(elem)

            # we cannot SMART_MERGE just add element to the list potentially we can do smart merge further
            # happens in the beggining or finding previous number or after some words in between numbers
            else: 
                found_num = elem
                all_nums.append(elem)

        # current element is not numerical it is either word in between numbers or in the beggining or ending of the list 
        # it all cases we cannot have non-numerical text in between number texts of the total number so we assume it is end of the number
        # without assigning current elem to the found_num variable 
        else:
            #if we have found num until now it is that total number 
            if found_num != '':
                founded_nums.append(found_num)
                new_converted_ls.append(found_num)

            # adding non numerical element to the final wanted list
            new_converted_ls.append(elem)
            #reset we will look for new number
            found_num = ''
            all_nums = []

    # after last iteration if we have found num which means we havent add it 
    # if we added it, found_num would be empty string ('')
    if found_num != '':
        founded_nums.append(found_num) 
        new_converted_ls.append(found_num) 

    return ' '.join(new_converted_ls)

def extract_entities(converted_list:list)->dict:
    """
    This function will extract the features it can and return them inside dictionary
    
    param:converted_list is final version of converted list where all text format numbers
    converted into numerical string 

    return: Python dictionary that contains extracted dates
    """
    #declearing the dictionary where founded entities will place
    entities_dict = dict()

    # iterate through converted list
    for elem in converted_list:
        # if element is numerical and bigger than 31 it is potentially indicating the year
        if elem.isnumeric() and int(elem) > 31:
            # if it is 4 digit it is okay to add directly to the dict
            if len(elem) == 4:
                entities_dict['year'] = elem
            
            # if it has length of 2 probably it is written in the shortened version
            elif len(elem) == 2:
                entities_dict['year'] = '19'+elem
            
            else: 
                # if we have element that is bigger than 31 and we have found year before as well 
                # year entity is not extractable for now just delete previous on as well
                if 'year' in entities_dict.keys():
                    entities_dict.pop('year')

        #if element is numerical and in between 0 and 31 it is potentially day
        elif elem.isnumeric() and (0<int(elem)<=31):
            # if we have already day entity delete it we are not sure about it
            if 'day' in entities_dict.keys():
                entities_dict.pop('day')
            else:
                entities_dict['day'] = elem
        
        # Find and add month as an entity
        elif get_close_matches(elem,MONTHS,cutoff=0.85):
            if 'month' in entities_dict.keys():
                print('FALLBACK')

            else:
                entities_dict['month'] = get_close_matches(elem,MONTHS,cutoff=0.85)[0]
            
        # if elem
    return entities_dict

def extract_date_dateparser(text):
    """Extracts a date from a string using the dateparser library.

    Args:
        text (str): The string to extract the date from.

    Returns:
        str: The extracted date in ISO format (YYYY-MM-DD), or None if no date was found.
    """

    # Define a list of common date formats to try parsing the input text with
    date_formats = date_formats = [
            '%Y-%m-%d',     # 1992-06-15
            '%d.%m.%Y',     # 15.06.1992
            '%d/%m/%Y',     # 15/06/1992
            '%m/%d/%Y',     # 06/15/1992
            '%Y.%m.%d',     # 1992.06.15
            '%Y/%m/%d',     # 1992/06/15
            '%m.%d.%Y',     # 06.15.1992
            '%m-%d-%Y',     # 06-15-1992   
            '%m/%d/%y',     # 06/15/92
            '%d.%m.%y',     # 15.06.92
            '%d/%m/%y',     # 15/06/92
            '%m.%d.%y',     # 06.15.92
            '%m-%d-%y',     # 06-15-92
            '%Y%m%d',       # 19920615
            '%y%m%d',       # 920615
            '%Y/%m/%d',     # 1992/06/15
            '%Y%m/%d',      # 199206/15
            '%Y-%m/%d',     # 1992-06/15
            '%Y%m-%d',      # 199206-15
            '%Y.%m/%d',     # 1992.06/15
            '%Y-%m-%d',     # 1992-06-15T00:00:00Z
            '%Y%m%dT%H%M%SZ',  # 19920615T080000Z
            '%Y-%m-%dT%H:%M:%SZ', # 1992-06-15T08:00:00Z
            '%Y-%m-%dT%H:%M:%S',  # 1992-06-15T08:00:00
            '%Y-%m-%dT%H:%M',  # 1992-06-15T08:00
            '%Y-%m-%dT%H',    # 1992-06-15T08
        ]
    # Attempt to parse the input text as a date using the defined date formats  
    date = dateparser.parse(text, date_formats=date_formats)

    # If a valid date was parsed, format it as YYYY-MM-DD and return it
    if date is not None:
        return date.strftime('%Y-%m-%d')
    
    # If parsing failed, return None
    return None


def format_entity_output(entity_dict):
    return f"{entity_dict['year']}:{entity_dict['month']}:{entity_dict['day']}"

test_texts = ['iki yuz uchuncu ilin on besh marti','doxsan sekkizin on besh marti','iki min uch on doqquz aprel','min doqquzuz on iki iyirmi besh aprel ','min doqquzuz doxsan bes, bes may','doxsan doqquzuncu il yirmi bes aprel ','doxsan besh on uch avqust','min doqquz yuz besh on iki dekabr']

while True:
    test_text = str(input('Write date please: '))
    print(test_text)
    splited = split_input(test_text,suffix_shorten_dict)
    converted = to_convert(splited)
    print(f"Converted form {converted}")

    extracted_entities = extract_entities(converted.split(' '))
    print(f'Extracted entities: ',extracted_entities)


    
    if is_three_numerical(converted.split(' ')):
        print('input',converted.replace(' ',''))
        three_nums_extraction = extract_date_dateparser(converted.replace(" ", ""))
        if three_nums_extraction != None:
            print("OUTPUT: ",three_nums_extraction)
        else: 
            print('please write in a normal way')
    else:
        print(extracted_entities)

    if extracted_entities == 3:
        format_entity_output(extracted_entities)

    print('\n\n\n\n')



    







                    


                    












