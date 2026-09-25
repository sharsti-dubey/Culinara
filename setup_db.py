"""
setup_db.py — Run once to create the database, table, and seed famous recipes.
Usage: python setup_db.py
"""
import pymysql
import json

ROOT_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "bhavya",          # ← change to your MySQL root password
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,   # ← FIX: allows row["cnt"] dict access
}

DB_NAME = "recipe_manager"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recipes (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    category     VARCHAR(60)  NOT NULL,
    cuisine      VARCHAR(60)  NOT NULL,
    difficulty   ENUM('Easy','Medium','Hard') NOT NULL DEFAULT 'Medium',
    prep_time    INT  NOT NULL DEFAULT 0,
    cook_time    INT  NOT NULL DEFAULT 0,
    servings     INT  NOT NULL DEFAULT 4,
    description  TEXT,
    ingredients  JSON NOT NULL,
    instructions JSON NOT NULL,
    tips         TEXT,
    tags         JSON,
    emoji        VARCHAR(8)   DEFAULT '🍽️',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

RECIPES = [
    {
        "name": "Spaghetti Carbonara",
        "category": "Italian",
        "cuisine": "Italian",
        "difficulty": "Medium",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "emoji": "🍝",
        "description": "A classic Roman pasta made with eggs, Pecorino Romano, guanciale, and black pepper. Silky, rich, and utterly satisfying.",
        "ingredients": [
            {"amount": "400g", "name": "spaghetti"},
            {"amount": "200g", "name": "guanciale or pancetta, diced"},
            {"amount": "4 large", "name": "eggs (2 whole + 2 yolks)"},
            {"amount": "100g", "name": "Pecorino Romano, finely grated"},
            {"amount": "50g", "name": "Parmesan, finely grated"},
            {"amount": "2 tsp", "name": "freshly cracked black pepper"},
            {"amount": "to taste", "name": "salt"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Bring a large pot of salted water to a boil and cook spaghetti until al dente (1 minute less than package directions)."},
            {"step_no": 2, "step": "While pasta cooks, fry guanciale in a cold skillet over medium heat, stirring until golden and crispy, about 8 minutes. Remove from heat."},
            {"step_no": 3, "step": "Whisk eggs, yolks, Pecorino, and Parmesan together in a bowl until smooth. Season generously with black pepper."},
            {"step_no": 4, "step": "Reserve 1 cup of pasta cooking water before draining. Drain pasta and immediately add to the pan with guanciale (off heat)."},
            {"step_no": 5, "step": "Pour egg mixture over pasta, tossing rapidly and adding pasta water a splash at a time to create a creamy, glossy sauce."},
            {"step_no": 6, "step": "Serve immediately with extra Pecorino and black pepper. Never add cream — the creaminess comes from the eggs!"}
        ],
        "tips": "Work quickly and keep the pan off heat when adding eggs to avoid scrambling. The sauce should coat the pasta like silk.",
        "tags": ["pasta", "classic", "roman", "no-cream", "quick"]
    },
    {
        "name": "Butter Chicken",
        "category": "Indian",
        "cuisine": "Indian",
        "difficulty": "Medium",
        "prep_time": 30,
        "cook_time": 40,
        "servings": 4,
        "emoji": "🍛",
        "description": "Murgh Makhani — tender chicken in a luscious tomato-cream sauce fragrant with warming spices. India's most beloved curry.",
        "ingredients": [
            {"amount": "800g", "name": "boneless chicken thighs, cubed"},
            {"amount": "1 cup", "name": "plain yogurt"},
            {"amount": "2 tsp", "name": "garam masala"},
            {"amount": "2 tsp", "name": "cumin powder"},
            {"amount": "1 tsp", "name": "turmeric"},
            {"amount": "1 tsp", "name": "chili powder"},
            {"amount": "3 tbsp", "name": "butter"},
            {"amount": "1 large", "name": "onion, finely chopped"},
            {"amount": "4 cloves", "name": "garlic, minced"},
            {"amount": "1 inch", "name": "ginger, grated"},
            {"amount": "400g", "name": "crushed tomatoes"},
            {"amount": "200ml", "name": "heavy cream"},
            {"amount": "1 tsp", "name": "sugar"},
            {"amount": "to taste", "name": "salt"},
            {"amount": "handful", "name": "fresh cilantro"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Marinate chicken in yogurt, half the spices, and salt for at least 2 hours (overnight is better)."},
            {"step_no": 2, "step": "Grill or broil marinated chicken at high heat until charred at the edges, about 10 minutes. Set aside."},
            {"step_no": 3, "step": "Melt butter in a heavy pan. Sauté onion until golden, about 10 minutes. Add garlic and ginger; cook 2 more minutes."},
            {"step_no": 4, "step": "Add remaining spices and cook for 1 minute until fragrant. Pour in crushed tomatoes and simmer 15 minutes."},
            {"step_no": 5, "step": "Blend the sauce until smooth (use an immersion blender). Return to heat, stir in cream and sugar."},
            {"step_no": 6, "step": "Add grilled chicken to the sauce and simmer 10 minutes. Adjust salt and garnish with cilantro. Serve with naan or basmati rice."}
        ],
        "tips": "Charring the chicken before adding to the sauce is the secret to authentic flavour. Don't skip this step!",
        "tags": ["curry", "chicken", "creamy", "indian", "popular"]
    },
    {
        "name": "Beef Bourguignon",
        "category": "French",
        "cuisine": "French",
        "difficulty": "Hard",
        "prep_time": 30,
        "cook_time": 180,
        "servings": 6,
        "emoji": "🥩",
        "description": "Julia Child's legendary French beef stew — slow-braised in red wine with mushrooms, pearl onions, and bacon. A masterpiece.",
        "ingredients": [
            {"amount": "1.5 kg", "name": "beef chuck, cut into 5cm cubes"},
            {"amount": "750ml", "name": "good red wine (Burgundy or Pinot Noir)"},
            {"amount": "200g", "name": "lardons or thick-cut bacon"},
            {"amount": "250g", "name": "mushrooms, quartered"},
            {"amount": "200g", "name": "pearl onions"},
            {"amount": "2 cups", "name": "beef stock"},
            {"amount": "2 tbsp", "name": "tomato paste"},
            {"amount": "3 cloves", "name": "garlic, smashed"},
            {"amount": "2", "name": "carrots, sliced"},
            {"amount": "1", "name": "bouquet garni (thyme, bay, parsley)"},
            {"amount": "2 tbsp", "name": "flour"},
            {"amount": "3 tbsp", "name": "olive oil"},
            {"amount": "to taste", "name": "salt and pepper"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Pat beef dry and season well. Brown in batches in hot oil until deeply caramelised on all sides. Remove to a plate."},
            {"step_no": 2, "step": "Fry lardons until golden. Add carrots, garlic, and cook 3 minutes. Stir in flour and tomato paste; cook 2 minutes."},
            {"step_no": 3, "step": "Pour in wine and stock, scraping up browned bits. Return beef, add bouquet garni. Bring to a simmer."},
            {"step_no": 4, "step": "Cover and braise in a 160°C (325°F) oven for 2.5 to 3 hours until beef is very tender."},
            {"step_no": 5, "step": "Meanwhile, sauté pearl onions in butter until golden. Sauté mushrooms separately until browned."},
            {"step_no": 6, "step": "Remove bouquet garni. Add onions and mushrooms to the stew. Simmer 10 minutes. Adjust seasoning and serve with crusty bread or mashed potatoes."}
        ],
        "tips": "Make it a day ahead — it tastes even better reheated! Use a wine you'd actually drink.",
        "tags": ["stew", "beef", "wine", "french", "slow-cook"]
    },
    {
        "name": "Pad Thai",
        "category": "Thai",
        "cuisine": "Thai",
        "difficulty": "Medium",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 2,
        "emoji": "🍜",
        "description": "Thailand's iconic stir-fried noodle dish with rice noodles, eggs, tofu or shrimp, bean sprouts, and a tangy tamarind sauce.",
        "ingredients": [
            {"amount": "200g", "name": "flat rice noodles (medium width)"},
            {"amount": "200g", "name": "shrimp or firm tofu"},
            {"amount": "2", "name": "eggs"},
            {"amount": "3 tbsp", "name": "tamarind paste"},
            {"amount": "2 tbsp", "name": "fish sauce"},
            {"amount": "1 tbsp", "name": "oyster sauce"},
            {"amount": "1 tbsp", "name": "sugar"},
            {"amount": "2 tbsp", "name": "vegetable oil"},
            {"amount": "3 cloves", "name": "garlic, minced"},
            {"amount": "2 stalks", "name": "green onions, chopped"},
            {"amount": "2 cups", "name": "bean sprouts"},
            {"amount": "50g", "name": "roasted peanuts, crushed"},
            {"amount": "1", "name": "lime, cut into wedges"},
            {"amount": "to garnish", "name": "cilantro and chili flakes"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Soak rice noodles in warm water for 20 minutes until pliable. Drain and set aside."},
            {"step_no": 2, "step": "Mix tamarind paste, fish sauce, oyster sauce, and sugar in a small bowl to make the sauce."},
            {"step_no": 3, "step": "Heat a wok over very high heat until smoking. Add oil and stir-fry shrimp or tofu until cooked. Push to the side."},
            {"step_no": 4, "step": "Add garlic, then crack eggs into the wok. Scramble quickly until just set."},
            {"step_no": 5, "step": "Add drained noodles and sauce. Toss everything together vigorously for 2-3 minutes."},
            {"step_no": 6, "step": "Add bean sprouts and green onions. Toss 30 seconds more. Plate and top with peanuts, lime wedges, and cilantro."}
        ],
        "tips": "A screaming hot wok is essential. Don't crowd the pan — cook in batches if needed.",
        "tags": ["noodles", "thai", "stir-fry", "quick", "street-food"]
    },
    {
        "name": "Chocolate Lava Cake",
        "category": "Dessert",
        "cuisine": "French",
        "difficulty": "Easy",
        "prep_time": 15,
        "cook_time": 12,
        "servings": 4,
        "emoji": "🍫",
        "description": "Warm, fudgy chocolate cakes with a molten center that flows like lava. A restaurant classic that's surprisingly easy to make at home.",
        "ingredients": [
            {"amount": "200g", "name": "dark chocolate (70%), chopped"},
            {"amount": "100g", "name": "unsalted butter"},
            {"amount": "3 large", "name": "eggs"},
            {"amount": "3", "name": "egg yolks"},
            {"amount": "100g", "name": "caster sugar"},
            {"amount": "50g", "name": "plain flour"},
            {"amount": "1 pinch", "name": "salt"},
            {"amount": "1 tsp", "name": "vanilla extract"},
            {"amount": "to serve", "name": "vanilla ice cream and powdered sugar"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Preheat oven to 220°C (425°F). Butter and flour 4 ramekins, tapping out excess."},
            {"step_no": 2, "step": "Melt chocolate and butter together in a double boiler or microwave in 30-second bursts. Stir until smooth."},
            {"step_no": 3, "step": "Whisk eggs, yolks, and sugar together until pale and slightly thickened, about 3 minutes."},
            {"step_no": 4, "step": "Fold the chocolate mixture into the egg mixture. Sift in flour and salt; fold gently until just combined."},
            {"step_no": 5, "step": "Divide batter among prepared ramekins. (Can be refrigerated up to 24 hours at this point.)"},
            {"step_no": 6, "step": "Bake 10-12 minutes until the edges are set but the center is still jiggly. Invert onto plates immediately and dust with powdered sugar. Serve with ice cream."}
        ],
        "tips": "The key is underbaking. 12 minutes is usually perfect, but test one first. Prepare ramekins the day before for stress-free entertaining.",
        "tags": ["chocolate", "dessert", "baking", "romantic", "quick"]
    },
    {
        "name": "Caesar Salad",
        "category": "American",
        "cuisine": "American",
        "difficulty": "Easy",
        "prep_time": 20,
        "cook_time": 10,
        "servings": 4,
        "emoji": "🥗",
        "description": "The king of salads — crisp romaine lettuce with a bold, garlicky dressing made with anchovies, lemon, Parmesan, and homemade croutons.",
        "ingredients": [
            {"amount": "2 heads", "name": "romaine lettuce, torn into pieces"},
            {"amount": "4 slices", "name": "thick bread, cubed (for croutons)"},
            {"amount": "4 cloves", "name": "garlic"},
            {"amount": "4 fillets", "name": "anchovy, mashed"},
            {"amount": "2 tsp", "name": "Dijon mustard"},
            {"amount": "2 tbsp", "name": "lemon juice"},
            {"amount": "1 tsp", "name": "Worcestershire sauce"},
            {"amount": "1", "name": "egg yolk"},
            {"amount": "100ml", "name": "olive oil"},
            {"amount": "80g", "name": "Parmesan, freshly grated"},
            {"amount": "to taste", "name": "salt and black pepper"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Make croutons: toss bread cubes with olive oil, 2 crushed garlic cloves, and salt. Bake at 190°C for 10-12 minutes until golden."},
            {"step_no": 2, "step": "Mash 2 garlic cloves with anchovies into a paste using a mortar and pestle."},
            {"step_no": 3, "step": "Whisk anchovy paste with mustard, Worcestershire, lemon juice, and egg yolk until combined."},
            {"step_no": 4, "step": "Slowly drizzle in olive oil while whisking constantly to emulsify into a creamy dressing."},
            {"step_no": 5, "step": "Season with salt and plenty of black pepper. Stir in most of the Parmesan."},
            {"step_no": 6, "step": "Toss romaine with dressing. Top with croutons and remaining Parmesan. Serve immediately."}
        ],
        "tips": "The dressing keeps in the fridge for 3 days. For a vegetarian version, skip anchovies and add capers.",
        "tags": ["salad", "classic", "lunch", "healthy", "quick"]
    },
    {
        "name": "Chicken Tikka Masala",
        "category": "Indian",
        "cuisine": "Indian",
        "difficulty": "Medium",
        "prep_time": 30,
        "cook_time": 30,
        "servings": 4,
        "emoji": "🫕",
        "description": "Britain's favourite curry — chargrilled chicken tikka simmered in a tangy, creamy tomato masala sauce. Vibrant, aromatic, irresistible.",
        "ingredients": [
            {"amount": "700g", "name": "boneless chicken breast, cubed"},
            {"amount": "200ml", "name": "yogurt"},
            {"amount": "2 tsp", "name": "tandoori masala"},
            {"amount": "1 tsp", "name": "kashmiri chili powder"},
            {"amount": "2 tbsp", "name": "ghee or oil"},
            {"amount": "1 large", "name": "onion, blended"},
            {"amount": "2 tsp", "name": "garam masala"},
            {"amount": "1 tsp", "name": "coriander powder"},
            {"amount": "400ml", "name": "crushed tomatoes"},
            {"amount": "150ml", "name": "heavy cream"},
            {"amount": "1 tsp", "name": "fenugreek leaves (kasuri methi)"},
            {"amount": "2 tbsp", "name": "butter"},
            {"amount": "to taste", "name": "salt"},
            {"amount": "handful", "name": "cilantro to garnish"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Marinate chicken with yogurt, tandoori masala, kashmiri chili, and salt for 4-8 hours."},
            {"step_no": 2, "step": "Thread chicken on skewers and grill or broil at high heat until slightly charred, about 10 minutes. Set aside."},
            {"step_no": 3, "step": "Heat ghee in a pan. Sauté onion paste until deep golden, about 15 minutes, stirring often."},
            {"step_no": 4, "step": "Add garam masala, coriander, and kashmiri chili. Stir 1 minute. Add crushed tomatoes; simmer 10 minutes."},
            {"step_no": 5, "step": "Stir in cream and butter. Crush fenugreek leaves between your palms and add — this is the signature aroma!"},
            {"step_no": 6, "step": "Add grilled chicken. Simmer 10 minutes. Garnish with cream swirl and cilantro. Serve with naan."}
        ],
        "tips": "Kasuri methi (dried fenugreek) is the secret ingredient that makes it taste authentic. Find it at any Indian grocery.",
        "tags": ["curry", "chicken", "popular", "british-indian", "creamy"]
    },
    {
        "name": "French Onion Soup",
        "category": "French",
        "cuisine": "French",
        "difficulty": "Medium",
        "prep_time": 15,
        "cook_time": 75,
        "servings": 4,
        "emoji": "🧅",
        "description": "Slowly caramelised onions in a rich beef broth, topped with crusty bread and a blanket of melted Gruyère. Pure Parisian warmth.",
        "ingredients": [
            {"amount": "1.5 kg", "name": "yellow onions, thinly sliced"},
            {"amount": "4 tbsp", "name": "unsalted butter"},
            {"amount": "1 tbsp", "name": "olive oil"},
            {"amount": "1 tsp", "name": "sugar"},
            {"amount": "2 cloves", "name": "garlic, minced"},
            {"amount": "150ml", "name": "dry white wine or dry sherry"},
            {"amount": "1.2 litres", "name": "good beef stock"},
            {"amount": "1", "name": "bouquet garni (thyme, bay leaf)"},
            {"amount": "1 tbsp", "name": "Worcestershire sauce"},
            {"amount": "4 thick slices", "name": "baguette or crusty bread"},
            {"amount": "200g", "name": "Gruyère cheese, grated"},
            {"amount": "to taste", "name": "salt and pepper"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Melt butter and oil in a heavy pot over medium-low heat. Add onions and a pinch of salt. Cook uncovered for 45-60 minutes, stirring occasionally, until deeply golden and caramelised."},
            {"step_no": 2, "step": "Add sugar and garlic; cook 5 minutes. Add wine to deglaze, scraping up the brown bits. Simmer until reduced by half."},
            {"step_no": 3, "step": "Pour in beef stock. Add bouquet garni and Worcestershire. Simmer 20 minutes. Season and remove bouquet garni."},
            {"step_no": 4, "step": "Preheat broiler. Ladle soup into oven-proof bowls placed on a baking sheet."},
            {"step_no": 5, "step": "Float a slice of bread on each bowl. Pile Gruyère generously on top."},
            {"step_no": 6, "step": "Broil 3-4 minutes until cheese is bubbling and golden-brown in spots. Serve immediately and carefully — bowls are extremely hot!"}
        ],
        "tips": "The caramelisation cannot be rushed. Low and slow — 60 minutes — is what develops the deep, sweet flavour.",
        "tags": ["soup", "french", "comfort", "cheese", "winter"]
    },
    {
        "name": "Vegetable Biryani",
        "category": "Indian",
        "cuisine": "Indian",
        "difficulty": "Hard",
        "prep_time": 30,
        "cook_time": 50,
        "servings": 6,
        "emoji": "🍚",
        "description": "Fragrant basmati rice layered with spiced vegetables and fried onions, sealed and slow-cooked by the dum method. A royal feast.",
        "ingredients": [
            {"amount": "3 cups", "name": "basmati rice, soaked 30 minutes"},
            {"amount": "500g", "name": "mixed vegetables (potato, carrot, peas, cauliflower)"},
            {"amount": "2 large", "name": "onions, thinly sliced"},
            {"amount": "1 cup", "name": "yogurt"},
            {"amount": "4 tbsp", "name": "ghee"},
            {"amount": "2", "name": "bay leaves"},
            {"amount": "4", "name": "green cardamom pods"},
            {"amount": "1 inch", "name": "cinnamon stick"},
            {"amount": "1 tsp", "name": "cumin seeds"},
            {"amount": "2 tsp", "name": "biryani masala"},
            {"amount": "1 tsp", "name": "saffron in 3 tbsp warm milk"},
            {"amount": "handful", "name": "fresh mint leaves"},
            {"amount": "handful", "name": "cilantro leaves"},
            {"amount": "to taste", "name": "salt"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Deep-fry sliced onions until dark golden and crispy. Drain on paper towels — these become the birista (fried onions)."},
            {"step_no": 2, "step": "Cook rice with whole spices (bay, cardamom, cinnamon) in salted water until 70% done (it should still have a bite). Drain."},
            {"step_no": 3, "step": "Sauté cumin in ghee. Add vegetables and biryani masala; cook 5 minutes. Stir in yogurt, half the fried onions, mint, and cilantro."},
            {"step_no": 4, "step": "In a large heavy pot, layer: vegetable masala first, then a layer of rice, drizzle of saffron milk and ghee."},
            {"step_no": 5, "step": "Cover tightly with foil then the lid (dum seal). Cook on medium heat 5 minutes, then very low heat for 25 minutes."},
            {"step_no": 6, "step": "Open and gently mix from the bottom up. Serve topped with remaining birista, cilantro, and mint. Pair with raita."}
        ],
        "tips": "The dum cooking (sealed steam) is what makes biryani perfect. Never lift the lid during cooking.",
        "tags": ["rice", "indian", "vegetarian", "festive", "aromatic"]
    },
    {
        "name": "Tiramisu",
        "category": "Dessert",
        "cuisine": "Italian",
        "difficulty": "Medium",
        "prep_time": 30,
        "cook_time": 0,
        "servings": 8,
        "emoji": "🍰",
        "description": "Italy's most famous dessert — ladyfingers soaked in espresso layered with a cloud-like mascarpone cream. Meaning 'pick me up' in Italian.",
        "ingredients": [
            {"amount": "500g", "name": "mascarpone cheese"},
            {"amount": "5", "name": "eggs, separated"},
            {"amount": "100g", "name": "caster sugar"},
            {"amount": "300ml", "name": "strong espresso, cooled"},
            {"amount": "2 tbsp", "name": "Marsala wine or coffee liqueur"},
            {"amount": "250g", "name": "savoiardi ladyfinger biscuits"},
            {"amount": "2 tbsp", "name": "high-quality cocoa powder"},
            {"amount": "1 pinch", "name": "salt"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Beat egg yolks with sugar until pale and fluffy, about 5 minutes. Fold in mascarpone until smooth and creamy."},
            {"step_no": 2, "step": "In a clean bowl, whisk egg whites with a pinch of salt until stiff peaks form."},
            {"step_no": 3, "step": "Gently fold the whipped egg whites into the mascarpone mixture in three additions, keeping it light and airy."},
            {"step_no": 4, "step": "Mix cooled espresso with Marsala. Quickly dip each ladyfinger in the coffee for 2 seconds per side (don't soak them)."},
            {"step_no": 5, "step": "Arrange a layer of soaked ladyfingers in a dish. Spread half the mascarpone cream on top. Repeat with another layer."},
            {"step_no": 6, "step": "Cover and refrigerate at least 4 hours (overnight is best). Dust generously with cocoa just before serving."}
        ],
        "tips": "Use room-temperature mascarpone to prevent lumps. Dip ladyfingers very briefly — soggy tiramisu is the most common mistake.",
        "tags": ["dessert", "italian", "no-bake", "coffee", "classic"]
    },
    {
        "name": "Margherita Pizza",
        "category": "Italian",
        "cuisine": "Italian",
        "difficulty": "Medium",
        "prep_time": 90,
        "cook_time": 12,
        "servings": 2,
        "emoji": "🍕",
        "description": "The Queen of pizzas — thin Neapolitan-style dough with San Marzano tomato sauce, fresh mozzarella, and basil. Simplicity perfected.",
        "ingredients": [
            {"amount": "300g", "name": "00 flour or bread flour"},
            {"amount": "190ml", "name": "lukewarm water"},
            {"amount": "7g", "name": "instant yeast"},
            {"amount": "1 tsp", "name": "salt"},
            {"amount": "1 tsp", "name": "olive oil"},
            {"amount": "400g", "name": "San Marzano tomatoes, crushed by hand"},
            {"amount": "1 clove", "name": "garlic, crushed"},
            {"amount": "250g", "name": "fresh mozzarella, torn"},
            {"amount": "handful", "name": "fresh basil leaves"},
            {"amount": "2 tbsp", "name": "extra-virgin olive oil"},
            {"amount": "to taste", "name": "salt and black pepper"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Mix flour, yeast, salt. Add water and olive oil; knead 10 minutes until smooth and elastic. Cover and rest 1 hour until doubled."},
            {"step_no": 2, "step": "Make sauce: simmer crushed tomatoes with garlic and a pinch of salt for 15 minutes. Remove garlic. Let cool."},
            {"step_no": 3, "step": "Place a baking stone or inverted baking sheet in the oven and preheat to maximum temperature (250°C / 500°F) for 45 minutes."},
            {"step_no": 4, "step": "Stretch dough gently by hand into a thin 30cm circle — never use a rolling pin, it deflates the bubbles."},
            {"step_no": 5, "step": "Spread a thin layer of tomato sauce leaving a 2cm border. Scatter torn mozzarella evenly."},
            {"step_no": 6, "step": "Bake on the hot stone for 10-12 minutes until the crust is charred in spots and cheese is bubbling. Top with fresh basil and a drizzle of olive oil."}
        ],
        "tips": "Oven temperature is everything. The hotter, the better. If you have a wood-fired oven, use it!",
        "tags": ["pizza", "italian", "vegetarian", "classic", "weekend"]
    },
    {
        "name": "Tom Yum Soup",
        "category": "Thai",
        "cuisine": "Thai",
        "difficulty": "Easy",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "emoji": "🍲",
        "description": "Thailand's iconic hot and sour prawn soup — intensely aromatic with lemongrass, galangal, kaffir lime, and a fiery chili kick.",
        "ingredients": [
            {"amount": "1 litre", "name": "chicken or prawn stock"},
            {"amount": "400g", "name": "large prawns, peeled"},
            {"amount": "200g", "name": "mushrooms, halved"},
            {"amount": "2 stalks", "name": "lemongrass, bruised and sliced"},
            {"amount": "5 slices", "name": "galangal or ginger"},
            {"amount": "6", "name": "kaffir lime leaves, torn"},
            {"amount": "3-5", "name": "Thai bird's eye chilies, crushed"},
            {"amount": "3 tbsp", "name": "fish sauce"},
            {"amount": "3 tbsp", "name": "lime juice"},
            {"amount": "1 tsp", "name": "sugar"},
            {"amount": "3 tbsp", "name": "Thai chili paste (nam prik pao)"},
            {"amount": "200ml", "name": "coconut milk (for Tom Kha variation)"},
            {"amount": "handful", "name": "cilantro"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Bring stock to a boil. Add lemongrass, galangal, and kaffir lime leaves. Simmer 5 minutes to infuse."},
            {"step_no": 2, "step": "Add mushrooms and chili paste; simmer 3 minutes."},
            {"step_no": 3, "step": "Add prawns and chilies. Cook just until prawns turn pink, about 2 minutes — don't overcook!"},
            {"step_no": 4, "step": "Season with fish sauce, lime juice, and sugar. Taste and adjust — it should be sour, spicy, and savoury in balance."},
            {"step_no": 5, "step": "Ladle into bowls and top with cilantro. Remove lemongrass and galangal before eating (they're flavouring only)."}
        ],
        "tips": "The balance of sour (lime), salty (fish sauce), and spicy (chili) is everything. Adjust to your taste.",
        "tags": ["soup", "thai", "spicy", "seafood", "quick"]
    },
    {
        "name": "Tacos al Pastor",
        "category": "Mexican",
        "cuisine": "Mexican",
        "difficulty": "Hard",
        "prep_time": 240,
        "cook_time": 25,
        "servings": 6,
        "emoji": "🌮",
        "description": "Mexico's legendary vertical-spit pork taco — marinated in chili and pineapple, served on corn tortillas with onion, cilantro, and salsa.",
        "ingredients": [
            {"amount": "1 kg", "name": "pork shoulder, thinly sliced"},
            {"amount": "4", "name": "guajillo chilies, soaked and deseeded"},
            {"amount": "2", "name": "ancho chilies, soaked and deseeded"},
            {"amount": "1 cup", "name": "pineapple juice"},
            {"amount": "3 tbsp", "name": "white vinegar"},
            {"amount": "1 tsp", "name": "cumin"},
            {"amount": "1 tsp", "name": "oregano"},
            {"amount": "4 cloves", "name": "garlic"},
            {"amount": "1 tbsp", "name": "achiote paste"},
            {"amount": "small", "name": "corn tortillas"},
            {"amount": "to serve", "name": "pineapple chunks, white onion, cilantro"},
            {"amount": "to serve", "name": "salsa verde or salsa roja"},
            {"amount": "to taste", "name": "salt and pepper"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Blend soaked chilies, pineapple juice, vinegar, garlic, cumin, oregano, achiote, and salt into a smooth marinade."},
            {"step_no": 2, "step": "Coat pork slices thoroughly in marinade. Refrigerate for at least 4 hours or overnight."},
            {"step_no": 3, "step": "Preheat a cast iron skillet or grill to very high heat."},
            {"step_no": 4, "step": "Cook pork in batches until caramelised and slightly charred at the edges, about 3-4 minutes per side."},
            {"step_no": 5, "step": "Chop the cooked pork roughly. Warm corn tortillas on a dry skillet or directly on a flame."},
            {"step_no": 6, "step": "Build tacos: tortilla, pork, onion, cilantro, pineapple, and salsa. Finish with a squeeze of lime."}
        ],
        "tips": "Marinate overnight for maximum flavour. The pineapple tenderises the meat and adds the signature sweet-savoury balance.",
        "tags": ["tacos", "mexican", "pork", "street-food", "festive"]
    },
    {
        "name": "Classic Ramen",
        "category": "Japanese",
        "cuisine": "Japanese",
        "difficulty": "Hard",
        "prep_time": 30,
        "cook_time": 180,
        "servings": 4,
        "emoji": "🍜",
        "description": "Rich, deeply flavoured tonkotsu-style ramen with a creamy pork bone broth, springy noodles, chashu pork, soft-boiled eggs, and nori.",
        "ingredients": [
            {"amount": "1.5 kg", "name": "pork trotters or neck bones"},
            {"amount": "400g", "name": "pork belly (for chashu)"},
            {"amount": "400g", "name": "fresh ramen noodles"},
            {"amount": "4", "name": "eggs"},
            {"amount": "4 tbsp", "name": "soy sauce"},
            {"amount": "2 tbsp", "name": "mirin"},
            {"amount": "2 tbsp", "name": "sake"},
            {"amount": "1 tbsp", "name": "sesame oil"},
            {"amount": "4 sheets", "name": "nori"},
            {"amount": "4 stalks", "name": "green onion, thinly sliced"},
            {"amount": "4 tbsp", "name": "miso paste (for tare)"},
            {"amount": "bamboo shoots", "name": "and corn to garnish"},
            {"amount": "to taste", "name": "salt and white pepper"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Blanch pork bones in boiling water 10 minutes. Drain and rinse well — this removes impurities and ensures a clear broth."},
            {"step_no": 2, "step": "Simmer blanched bones in fresh water on medium heat for 3 hours until broth is creamy and milky white. Season with salt."},
            {"step_no": 3, "step": "Make chashu: roll pork belly tightly, secure with twine. Braise in soy, mirin, sake, and water for 90 minutes."},
            {"step_no": 4, "step": "Soft-boil eggs for 6.5 minutes, then marinate in leftover chashu braising liquid for 2 hours."},
            {"step_no": 5, "step": "Mix miso paste with sesame oil and a ladle of hot broth to make the tare. Place 1 tbsp tare in each bowl."},
            {"step_no": 6, "step": "Cook noodles per package. Add to bowls, ladle over hot broth. Top with sliced chashu, halved marinated egg, green onion, nori, and bamboo shoots."}
        ],
        "tips": "The broth is the hero — it needs time. Make the broth and chashu the day before; assemble just before serving.",
        "tags": ["ramen", "japanese", "noodles", "pork", "weekend"]
    },
    {
        "name": "Shakshuka",
        "category": "American",
        "cuisine": "Middle Eastern",
        "difficulty": "Easy",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "emoji": "🍳",
        "description": "Eggs poached in a spiced tomato and pepper sauce — the ultimate one-pan brunch that's as beautiful as it is delicious.",
        "ingredients": [
            {"amount": "6", "name": "large eggs"},
            {"amount": "800g", "name": "crushed tomatoes"},
            {"amount": "2", "name": "red bell peppers, diced"},
            {"amount": "1 large", "name": "onion, diced"},
            {"amount": "4 cloves", "name": "garlic, minced"},
            {"amount": "2 tsp", "name": "smoked paprika"},
            {"amount": "1 tsp", "name": "cumin"},
            {"amount": "½ tsp", "name": "chili flakes"},
            {"amount": "2 tbsp", "name": "olive oil"},
            {"amount": "100g", "name": "feta cheese, crumbled"},
            {"amount": "handful", "name": "fresh parsley"},
            {"amount": "to serve", "name": "crusty bread"}
        ],
        "instructions": [
            {"step_no": 1, "step": "Heat olive oil in a large oven-safe skillet over medium heat. Sauté onion and peppers until softened, about 8 minutes."},
            {"step_no": 2, "step": "Add garlic, paprika, cumin, and chili flakes. Cook 1 minute until fragrant."},
            {"step_no": 3, "step": "Pour in crushed tomatoes. Season with salt and pepper. Simmer 10 minutes until sauce thickens slightly."},
            {"step_no": 4, "step": "Make 6 wells in the sauce. Crack an egg into each well. Sprinkle with feta."},
            {"step_no": 5, "step": "Cover and cook on low heat for 8-10 minutes until whites are set but yolks are still runny (or as preferred)."},
            {"step_no": 6, "step": "Scatter fresh parsley on top and serve directly from the pan with crusty bread to mop up the sauce."}
        ],
        "tips": "Cover the pan for the last few minutes to steam the egg whites without overcooking the yolks.",
        "tags": ["eggs", "brunch", "vegetarian", "one-pan", "quick"]
    }
]


def setup():
    # Connect without specifying DB first
    con = pymysql.connect(**ROOT_CONFIG)
    try:
        with con.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4")
            cur.execute(f"USE `{DB_NAME}`")
            cur.execute(CREATE_TABLE_SQL)

            # Check existing count
            cur.execute("SELECT COUNT(*) as cnt FROM recipes")
            existing = cur.fetchone()["cnt"]
            if existing >= len(RECIPES):
                print(f"✅  Database already has {existing} recipes. Skipping seed.")
                return

            cur.execute("TRUNCATE TABLE recipes")

            sql = """
                INSERT INTO recipes
                  (name, category, cuisine, difficulty, prep_time, cook_time,
                   servings, description, ingredients, instructions, tips, tags, emoji)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            for r in RECIPES:
                cur.execute(sql, (
                    r["name"], r["category"], r["cuisine"], r["difficulty"],
                    r["prep_time"], r["cook_time"], r["servings"], r["description"],
                    json.dumps(r["ingredients"]), json.dumps(r["instructions"]),
                    r["tips"], json.dumps(r["tags"]), r.get("emoji", "🍽️")
                ))
            con.commit()
            print(f"✅  Inserted {len(RECIPES)} famous recipes into `{DB_NAME}`.")
    finally:
        con.close()


if __name__ == "__main__":
    setup()