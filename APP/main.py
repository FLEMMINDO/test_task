from fastapi import FastAPI

# from APP.routers import (categories, products, users, reviews, cart, orders, payments, support_chats,
#                         games, attributes, attribute_options, product_attribute_values, product_media)


app = FastAPI(
    title="Test_task_Dimatech",
    version="1.0",
    description="For payments"
)

# app.include_router(categories.router)
# app.include_router(products.router)
# app.include_router(users.router)
# app.include_router(reviews.router)
# app.include_router(cart.router)
# app.include_router(orders.router)
# app.include_router(payments.router)
# app.include_router(support_chats.router)
# app.include_router(games.router)
# app.include_router(attributes.router)
# app.include_router(attribute_options.router)
# app.include_router(product_attribute_values.router)
# app.include_router(product_media.router)


@app.get("/")
async def root():
    """
    Корневой маршрут
    """
    return {"message": "API payments"}
