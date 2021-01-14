from core import image_generation, recipe_ingredients
from parse import cocktail_ingredients, parse_ingredients
from drivers import fb_driver, unsplash_driver, pexels_driver
from utils import io_ops, filepaths
from utils.emojis import emojis_pycode

ingredients_list = parse_ingredients.get_ingredients_list()

ordinal = lambda n: "%d%s" % (
    n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

page_id = io_ops.get_env_var("recipe_page_id")
recipe_access_token = io_ops.get_env_var("recipe_access_token")

cocktail_id = io_ops.get_env_var("cocktail_page_id")
cocktail_access_token = io_ops.get_env_var("cocktail_access_token")

ingredient = recipe_ingredients.Ingredients()
fb = fb_driver.FbDriver()


def post_recipe_sample(k=3):
    ingredient = recipe_ingredients.Ingredients()
    samples = ingredient.get_good_combinations(1, 3)[0]

    message = ""
    for i in range(k):
        message += f"{ordinal(i + 1)} ingredient: {samples[i]}\n"

    keywords = " ".join(samples)
    success, picture_text = unsplash_driver.get_picture_by_keywords(keywords,
                                                                    filepaths.recipe_rawpic_file)

    post_text = f"{message}\nPicture {picture_text}"
    print(post_text)

    if success:
        image_generation.label(filepaths.recipe_rawpic_file, samples,
                               filepaths.recipe_newpic_file)
        return fb.post_picture(recipe_access_token, post_text,
                               filepaths.recipe_newpic_file)
    else:
        return fb.post_text_http_request(page_id, recipe_access_token,
                                         post_text)


def post_cocktail_sample():
    cocktail_fb = fb_driver.FbDriver(access_token=cocktail_access_token)
    flatten = lambda l: [item for sublist in l for item in sublist]

    sample = cocktail_ingredients.get_ingredients()
    message = cocktail_ingredients.generate_sentence(sample)

    keywords = ' '.join(flatten(sample))
    success, picture_text = unsplash_driver.get_picture_by_keywords(keywords,
                                                                    filepaths.cocktail_rawpic_file)
    post_text = f"{message}\nPicture {picture_text}"
    print(post_text)

    if success:
        image_generation.label(filepaths.cocktail_rawpic_file,
                               list(map(lambda s: s.capitalize(),
                                        flatten(sample)[:3])),
                               filepaths.cocktail_newpic_file)

        return cocktail_fb.post_picture(post_text,
                                        filepaths.cocktail_newpic_file)
    else:
        return cocktail_fb.post_text_http_request(page_id, post_text)


def get_versus_post_content():
    """
    # Emojis
    Python Source Code come from https://www.fileformat.info/info/unicode/char

    # Facebook Reactions
    Facebook Reacts are of type enum {NONE, LIKE, LOVE, WOW, HAHA, SORRY, ANGRY}
    Care reactions are counted as Like reactions (ref https://developers.facebook.com/docs/graph-api/reference/v9.0/object/reactions)
    """
    samples = ingredient.get_random_versus_combination(set_length=2)
    print(samples)
    first_ing, second_ing, third_ing = [sample.capitalize() for sample in
                                        samples]
    # TODO: Update i_versus
    post_text = f"VERSUS TIME! over the {first_ing.upper()}.\r\n" \
        "Which is the best duo?\r\n" \
        f"{emojis_pycode.orange_heart} LOVE REACT: " \
        f"{first_ing} + {second_ing}\r\n" \
        f"{emojis_pycode.open_mouth} WOW REACT: " \
        f"{first_ing} + {third_ing}\r\n\r\n" \
        "Who will win?\r\n\r\n" \
        "You have 48 hours to decide!\r\n\r\n"

    success, picture_1_text = pexels_driver.get_picture_by_keywords(
        [second_ing], filepaths.versus1_img)

    if not success:
        print("Did not find picture for", second_ing)
        return post_recipe_versus()

    success, picture_2_text = pexels_driver.get_picture_by_keywords(
        [third_ing], filepaths.versus2_img)

    if not success:
        print("Did not find picture for", third_ing)
        return post_recipe_versus()

    post_text += f"Picture of {second_ing} {picture_1_text}\r\n"
    post_text += f"Picture of {third_ing} {picture_2_text}\r\n"

    post_text += "#food_versus #food #recipe #cook #tasty #cooking #foodie"
    post_text += " #foodversus #foodlover #healthy"
    for ingredient_name in [first_ing, second_ing, third_ing]:
        keywords = ingredient_name.lower().split(" ")
        for k in keywords:
            post_text += f" #{k}"

    # Use versus generator image
    img_text = [f"What's tastier?\r\n{first_ing} with...",
                second_ing, third_ing]
    image_generation.versus_label([filepaths.versus1_img,
                                   filepaths.versus2_img],
                                  img_text, filepaths.recipe_newpic_file)

    # Post, get post id
    return samples, post_text, filepaths.recipe_newpic_file


def post_recipe_versus():
    samples, post_text, image_path = get_versus_post_content()
    response = fb.post_picture(post_text, filepaths.recipe_newpic_file)

    ingredient.add_to_pending(response['post_id'], *samples)


def validate_versus_post():
    ok = False
    while not ok:
        samples, post_text, image_path = get_versus_post_content()
        print(post_text)
        answer = input("Are you ok with posting this? (y/n)")
        if answer == 'y':
            ok = True

    response = fb.post_picture(post_text, filepaths.recipe_newpic_file)
    print(response)
    ingredient.add_to_pending(response['post_id'], *samples)


if __name__ == '__main__':
    # print(post_cocktail_sample())
    # print(post_recipe_sample())
    # print(post_recipe_versus())
    # get_versus_post_content()
    validate_versus_post()
