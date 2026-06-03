# def mianfun():
#     print('mianfun')
#     def subfun():
#         print('subfun')
#
#     subfun()
#
# mianfun()


def mianfun():
    a = subfun()
    print(a)
    return 'mainfun' + a


def subfun():
    return 'subfun'


print(mianfun())
