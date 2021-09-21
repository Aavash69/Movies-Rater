list = [5,3,7,9,1,8]

new_list = []



while list != []:

    standard = 0
    for number in list:
        if number > standard:
            standard = number

    new_list.append(standard)
    list.remove(standard)




print(new_list[-1::-1])
