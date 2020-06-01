from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# helper function to convert scraped contacts to standard format
def convert_to_vCard(contact):
    return "\n".join([
        "BEGIN:VCARD",
        "VERSION:4.0",
        "N:{last};{first};".format(**contact),
        "FN:{first} {last}".format(**contact),
        "TEL;TYPE=cell:{number}".format(**contact),
        "END:VCARD",
    ])

# the site uses ember and renames html tags to prevent scraping
# we get around this by referring to structure of the page
# for example, instead of ember355 (which will frequently be relabeled to something like ember299)
# we find the structure of the element in tags

print("Email: ")
user = input()
print("Password: ")
password = input()
print("Device Number: (Which light phone are we collecting contacts from? If you have one phone, answer 1)")
device_num = int(input()) - 1 # this is one indexed for usability?

# set the headless option so that the browser runs in the background
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

# go to main page
driver.get("https://dashboard.thelightphone.com")

# login
form = driver.find_element_by_tag_name("form")
inputs = form.find_elements_by_tag_name("input")
inputs[0].send_keys(user) # username input
inputs[1].send_keys(password) # password input
form.submit()

# click phone tab to retrieve device page
driver.find_element_by_css_selector("body>div>div>div>ul>li").click()

# click specific device button
driver.find_elements_by_css_selector("body>div>div>div>div>ul>li")[device_num].click()

# click contacts button
driver.find_element_by_css_selector("body>div>div>div>ul>li").click()

# click edit contacts button
driver.find_elements_by_css_selector("body>div>div>div>ul>li")[2].click()

# get contacts buttons, and then convert buttons to contact links
buttons = driver.find_elements_by_css_selector("body>div>div>div>ul>div>li")
links = [button.find_elements_by_tag_name("a")[1].get_attribute("href") for button in buttons]

# iterate through contact links then retrieve first name, last name, and number for each
contacts = []
for link in links:
    driver.get(link)
    fields = driver.find_elements_by_css_selector("form>div>div>input")
    contacts.append({
        "first" : fields[0].get_attribute("value"),
        "last"  : fields[1].get_attribute("value"),
        "number"     : fields[2].get_attribute("value"),
    })

# save .vcf file for contact upload
with open("light_phone_exported_contacts.vcf", "w") as f:
    f.write("\n\n".join(map(convert_to_vCard, contacts)))
