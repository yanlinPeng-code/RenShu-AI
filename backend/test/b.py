import jwt
print("PyJWT 版本：", jwt.__version__)  # 官方库会输出版本号（如 2.8.0）
print("是否有 encode 方法：", hasattr(jwt, "encode"))  # 官方库必返回 True