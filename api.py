from flask import Flask, jsonify, request
from fuzzywuzzy import fuzz, process
import pydash
import json

#initialize the list that will contain the data
all = []

with open('mobiles-data.json') as json_file:
    #get all the mobile data from json file and store in the list
    all = json.load(json_file)

def getNumbersFromStr(str):
    numbers = []
    nums = str.split('.')
    for num in nums:
        numbers.append(''.join([n for n in num if n.isdigit()]))
    res = ''
    if len(numbers) > 1:
        res = numbers[0] + '.' + numbers[1]
    else:
        res = numbers[0]
    if res == '':
        return 0
    else:
        return float(res)

app = Flask(__name__)

def getPriceRange(price):
    price = float(price)
    return [price + (30*price)/100, price - (30*price)/100]

@app.route('/')
def getAll():
    return jsonify({'data' : all, 'Data-length' : len(all)})

# call '/mobiles/{id}' where id is mobile id and view only that example '/mobiles/2'
@app.route('/mobiles/<int:id>', methods=['GET'])
def getById(id):
    result = []
    for mobile in all:
        if mobile['id'] == id:
            result = mobile
            break
    return jsonify({'data' : result})

#search api example '/search/search?query=iphone+13+pro+max+256gb+sierra&price=4000'
@app.route("/search/<section>")
def data(section):
    assert section == request.view_args['section']
    args = request.args.to_dict(flat=True)
    price = args['price'] if args['price'] else 0
    priceRange = getPriceRange(price)
    max = float(priceRange[0])
    min = float(priceRange[1])
    
    query = args['query'] if args['query'] else ''
    first3 = ''
    after3 = ''
    arr = query.split(' ')
    length = len(arr)
    if (length > 3):
        for i in range(0, 3):
            first3 = first3 + ' ' + arr[i]
        for i in range(3, length):
            after3 = after3 + ' ' + arr[i]
    else:
        for i in range(0, len(arr)):
            first3 = first3 + ' ' + arr[i]
    first3 = first3.strip()
    after3 = after3.strip()

    result = []

    mobile_names_dict = dict(enumerate([mobile['mobile_name'] for mobile in all]))
    best_mobiles = process.extractBests(query.lower(), mobile_names_dict, score_cutoff=70, limit=10)
    result = [all[z] for (x,y,z) in best_mobiles]
    
    if len(after3) != 0:
        mobile_names_dict = dict(enumerate([mobile['mobile_name'] for mobile in result]))
        best_mobiles = process.extractBests(after3.lower(), mobile_names_dict, score_cutoff=30, limit=10)
        result = [result[z] for (x,y,z) in best_mobiles]

    finalResult = result

    if price != 0:
        finalResult = []
        for mobile in result:
            price = getNumbersFromStr(mobile['mobile_price'])
            if price <= max and price >= min:
                finalResult.append(mobile)

    # uniq = pydash.arrays.uniq_by(finalResult, lambda val: val['id'] == finalResult['id'])
    return jsonify({'Data-length': len(finalResult),'data' : finalResult, "max" : {'max': max, 'min': min}})


# call '/site/noon' to display all the mobile data from 'noon' site only, similar for 'sharafdg'
@app.route('/site/<string:site>/')
def getBySite(site):
    result = []
    for mobile in all:
        if mobile['site'] == site:
            result.append(mobile)
            break
    return jsonify({'data' : result})


if __name__ == "__main__":
    app.run(debug=True)