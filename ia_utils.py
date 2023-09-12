# Imports
import pyautogui
from time import sleep
from datetime import datetime
import cv2
from datetime import datetime  
import numpy as np
import pyperclip
from waiting import wait
import keyboard
import openai

# Open AI Key
openai_api_key='ENTER OPEN_AI_API_KEY HERE'

### Collection of utility functions
def ts_print(input_str):
    
    # Get Current Time
    str_date_time = datetime.now().strftime("[%Y-%m-%d - %H:%M:%S]")
    print(f"{str_date_time} {input_str}")


def locate_image(path_to_image, path_to_template, threshold=0.8):
    ''' Locates position of template in an image. Returns X/Y at center of the position match'''

    # Load Image & Template
    image = cv2.imread(path_to_image)
    template = cv2.imread(path_to_template)

    # Raise Error
    if image is None:
        raise ValueError(f"Failed to load the image {path_to_image}.")
        
    if template is None:
        raise ValueError(f"Failed to load the template image or {path_to_template}.")

    # Conver to gray scale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Perform matching
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Adjust this value for desired similarity threshold
    threshold = threshold  
    if max_val >= threshold:
        template_height, template_width = template_gray.shape
        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)

        # Return the middle point of the matched pattern, else return None
        x_pos = int(np.mean([top_left[0], bottom_right[0]]))
        y_pos = int(np.mean([top_left[1], bottom_right[1]]))
        return x_pos, y_pos
    else:
        return None, None
    

def ez_locate_image(path_to_image, path_to_template, image_default_folder='./tmp/', template_default_folder='./resources/'):
    
    ''' Simple wrapper around locate images that adds default paths and .png to the files to make the code easier to read.'''
    screenshot_path = f'{image_default_folder}{path_to_image}.png'
    smaller_image_path = f'{template_default_folder}{path_to_template}.png'

    return locate_image(screenshot_path, smaller_image_path)



def ez_locate_image_any(image, template_list):
    ''' Searches for ANY match between image and templates in template list. Breaks as soon as ANY template is found.'''

    for template in template_list:
        x, y = ez_locate_image(image, template)
        
        # Cancel Loop if we find something. Return values
        if x is not None:
            break

    return x,y

def move_cursor(x, y, do_click=False, delay=(0.3, 0.5)):
    ''' Moves Mouse Cursor to x,y position and clicks if do_click=True'''
    if x is not None:
        # Print
        #ts_print(f'Moved Cursor to position X:{x}-Y:{y}')
        pyautogui.moveTo(x, y)
        
        if do_click:
            #ts_print(f'Clicked position X:{x}-Y:{y}')
            sleep(np.random.uniform(delay[0], delay[1]))
            pyautogui.click()


def move_cursor_default_position(do_click=False):
    ''' Moves the cursor to some default position on the screen (i.e. the instagram camera/logo)'''
    x, y = ez_locate_image_any('snapshot', ['instagram_camera_icon', 'instagram_logo'])
    move_cursor(x, y, do_click=do_click)
    

def get_page_source_code(wait_duration=2):
    ''' Presses CTRL + U in Google Chrome to open the source code in a new tab. Copies content, closes tab again and returns source code as string.
        wait_duration allows to wait a few seconds in case loading of source code takes time.'''

    # Press CTRL + to open source sode
    pyautogui.keyDown('ctrl')
    pyautogui.press("u")
    pyautogui.keyUp('ctrl')
    sleep(wait_duration)

    # Select everything
    pyautogui.keyDown('ctrl')
    pyautogui.press("a")
    pyautogui.keyUp('ctrl')

    # Copy everything
    pyautogui.keyDown('ctrl')
    pyautogui.press("c")
    pyautogui.keyUp('ctrl')

    # Retrieve Source_Code from Clipboard 
    source_code = pyperclip.paste()

    # Close Tab
    pyautogui.keyDown('ctrl')
    pyautogui.press("w")
    pyautogui.keyUp('ctrl')

    return source_code


def username_from_source_code(source_code):
    ''' Extracts username from the homepage of a user by reading the source code.'''

    # Used to determine first occurence of username in source code
    onset_string = 'href="https://www.instagram.com/'
    offset_string = ' hreflang="x-default'
    
    # Find Pos
    onset_pos = source_code.find(onset_string)
    offset_pos = source_code.find(offset_string)

    # Find Username
    username = source_code[onset_pos+len(onset_string):offset_pos-2]

    return username


def take_screenshot(region=(0, 0, 2560, 1440), file_name='./tmp/snapshot.png', verbose=True):
    
    ''' Function that takes a screenshot'''
    if verbose:
        ts_print(f'Created Screenshot: {file_name}.')
    screenshot = pyautogui.screenshot(file_name, region=region) # Images + List
    return screenshot


def check_for_instagram():
    ''' Simple Function that checks if the instagram logo or the instagram camera icon is on the screen'''

    # To avoid overwriting existing file
    snapshot2 = take_screenshot(file_name='./tmp/snapshot2.png')

    # Check if there
    x, y = ez_locate_image_any('snapshot2', ['instagram_camera_icon', 'instagram_logo', 'colored_insta_icon_check'])

    if x is not None:
        return True
    else:
        ts_print('Could not locate instagram website.')
        return False
    

def perform_search(hashtag):
    ''' Enters search term into search bar'''
    # Write Hashtag
    keyboard.write('#')

    # Types Word by Word.
    for letter in hashtag:
        keyboard.write(letter)
        sleep(np.random.uniform(0.05, 0.15))

    sleep(0.1)
    pyautogui.press('enter')


def select_first_result():
    ''' Uses the big SEARCH text above the search bar as guiding point to click on the first search result in the list'''
    
    screenshot = take_screenshot()
    x,y = ez_locate_image_any('snapshot', ['search_text'])
    move_cursor(x, y+250, do_click=True)


def rndm(a, b):
    # Wrapper around numpy function
    return np.random.uniform(a, b)


def like_post():
    ''' Looks for icon group below posts and clicks on the heart. '''
    x, y = ez_locate_image('snapshot', 'white_like')
    move_cursor(x, y, do_click=True)


def check_posts_allowed():
    ''' Checks if posts are allowed under this post. '''
    x, y = ez_locate_image('snapshot', 'posts_not_allowed')

    if x is None:
        return True
    else:
        ts_print('Posts are not allowed on this comment.')
        return False

def move_to_image_position(n):#
    ''' Has hardcoded the positions of images and moves cursor to one of the six positions.'''

    # Hard coded image positions
    post_position = np.array([[[960, 735], [1450, 735], [1900, 735]], [[960, 1200], [1450, 1200], [1900, 1200]]])
    position_list = []
    for row in range(0,2):
        for column in range(0,3):
            position_list.append(post_position[row,column,:])

    x, y = position_list[n]
    move_cursor(x, y, do_click=True); sleep(rndm(0.3, 0.5))


def get_completion(prompt, model="gpt-3.5-turbo", temperature=1):

    # Helper Function to Query ChatGPT
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature)
    return response.choices[0].message["content"]


def query_gpt_for_commment():
    ''' Creates a comment using ChatGPT. '''

    prompt = f"""You are a social media expert with 10 years experience on instagram.
    You are primarily engaging with content related about cute animals, such as dogs and puppies. 
    You are commenting on posts from followers and other instagram users, primarily with the purpose of engaging with them and making them follow your account.
    You are always kind and nice and respectful.
    Make sure that youre response is between two to three sentences long and feel free to use emojis.
    Make also sure that you do not include quotation marks at the beginning or the end of the prompt.
    Last, do not ask explicitly for people to follow you.

    Your task is write to a comment to an instagram post that shows a cute dog.
    """
    response = get_completion(str(prompt))

    ts_print(f'[Created Comment]: {response}')

    return response

def initiate_comment():
    x, y = ez_locate_image('snapshot', 'add_a_comment_field')
    move_cursor(x, y, do_click=True)

def write_and_post_comment(comment):

    # Check First if Comments are allowed
    if check_posts_allowed():
    
        ''' Enters search term into search bar'''
        # Write Hashtag
        keyboard.write('#')

        for letter in comment:
            keyboard.write(letter)
            sleep(np.random.uniform(0.05, 0.15))

        # Now Click on Post button
        x, y = ez_locate_image('snapshot', 'blue_post_button')
        move_cursor(x, y, do_click=True)


def follow_user_from_post():
    ''' Clicks on the follow button when writing a post.'''
    x, y = ez_locate_image('snapshot', 'blue_post_follow_button')
    move_cursor(x, y, do_click=True)


def close_post():

    ''' Closes Post Website'''
    x, y = ez_locate_image('snapshot', 'post_close_icon')
    move_cursor(x, y, do_click=True)
    sleep(rndm(0.5, 1))


def search_for_symbol(check_symbol):
    ''' Symbol search for symbol on screenshot. Returns True / False'''

    # Take Screenshot
    screenshot = take_screenshot(file_name='./tmp/snapshot.png', verbose=False); 
    
    # Search for Symbol
    x, y = ez_locate_image('snapshot', check_symbol)

    # Boolean Return
    if x:
        return True
    else:
        return False
    

def wait_for_page(check_symbol, timeout_seconds=20):
    
    ''' Checks if a webpage has loaded by taking screenshots and searching for check_symbol. 
    If check_symbol is found, it returns True, else it return False'''
    wait(lambda: search_for_symbol(check_symbol), timeout_seconds=timeout_seconds)


def goto_hashtag_page(hashtag):
    ''' Opens Instagram website for hashtag. '''

    # Define Target URL
    target_url = f'https://www.instagram.com/explore/tags/{hashtag}/'

    # Select Chrome Search Bar
    x, y = ez_locate_image('snapshot', 'chrome_search_bar_icons')
    move_cursor(x-400, y, do_click=True)

    # Enter Target Url
    keyboard.write(target_url)
    pyautogui.press('enter')

    # Wait until page is displayed
    sleep(3) # In case we are alreayd on a page with the symbol, we need to wait a little bit.
    wait_for_page('posts2') 


def read_commments():

    # Retrieve Source Code
    source_code = get_page_source_code()

    # Used to determine first occurence of username in source code
    onset_string = '{"articleBody":"'
    offset_string = ' hreflang="x-default'
    
    # Find Pos
    onset_pos = source_code.find(onset_string)
    offset_pos = source_code.find(offset_string)

    # Return Comment
    comment = source_code[onset_pos+len(onset_string):offset_pos-2]

    return comment

def read_commments():

    ''' Retrieves comment text from page source code of a post'''

    # Retrieve Source Code
    source_code = get_page_source_code()

    # Used to determine first occurence of username in source code
    onset_string = '{"articleBody":"'
    offset_string = '"author":{'
    
    # Find Pos
    onset_pos = source_code.find(onset_string)
    offset_pos = source_code.find(offset_string)

    # Return Comment
    comment = source_code[onset_pos+len(onset_string):offset_pos-2]

    # TODO: Format String properly to avoid smileys etc.

    return comment


def clean_comment(comment):
    ''' Cleans a comment from special characters using ChatGPT. '''

    prompt = f"""The following string contains the text of an instagram post. It still contains unicode inside that represents emojis or other characters.

        Please clean the following string from those characters:

        Text: 'It\\u2019s my brother E.T \\ud83d\\udc7d\\ud83d\\udc36\\n-\\n\\ud83d\\udcf8 Via \\ud83d\\udcf7 \\u0040pugofficial60\\n\\n-\\nFollow \\ud83d\\udc49 \\u0040pugloverfamily for more content\\ud83d\\udc93\\ud83c\\udf3c\\ud83e\\udd70\\n=======================\\nFollow \\ud83d\\udc49 \\u0040pugloverfamily for more content\\ud83d\\udc93\\ud83c\\udf3c\\ud83e\\udd70\\n-\\n-\\n-\\n-\\n#pugrequest#carlin#puglyfe#pugsandkisses#cutepugs#pugworld#pugsofinsta#thetomcoteshow#pugsrequest#ilovemypug#puglove'

        Answer: 'Its my brother E.T Via pugofficial60 Follow pugloverfamily for more content Follow pugloverfamily for more content #pugrequest#carlin#puglyfe#pugsandkisses#cutepugs#pugworld#pugsofinsta#thetomcoteshow#pugsrequest#ilovemypug#puglove'

        Text: "{str(comment)}

        Answer: 
    """
    response = get_completion(prompt)

    ts_print(f'[Cleaned Comment]: {response}')

    return response


