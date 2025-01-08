# YÊU CẦU BÀI TOÁN

## Dùng superset API để thực hiện các bước tạo nên 1 biểu đồ với đầu vào là một file excel -> đầu ra là 1 biểu đồ trên superset

### Các bước chạy chương trình

* Chạy môi trường ảo

```
source/venv/bin/activate
```

* Khởi động superset

  ```
  export TAG=3.1.1
  docker compose -f docker-compose-image-tag.yml up
  ```
* Khởi động database (postgres)

  ```
  docker compose up -d
  ```
* Chạy fastapi

  ```
  uvicorn main:app --reload
  ```

Để tạo 1 biểu đồ, trước hết  hãy vào giao diện superset và kết nối với database bằng cách vào setting -> database connection -> connet to postgres -> sau đó lấy id
