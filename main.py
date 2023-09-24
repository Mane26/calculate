import asyncio
from typing import Optional

from fastapi import FastAPI

app = FastAPI()

# Словарь для хранения фоновых задач и их результатов
background_tasks = {}


@app.post("/calculate")
async def calculate(x: int, y: int, operator: str):
    operations = {
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "*": lambda x, y: x * y,
        "/": lambda x, y: x / y
    }
    if operator not in operations:
        return {"error": "Недопустимый оператор"}

    # Генерируем уникальный идентификатор задачи
    task_id = len(background_tasks) + 1

    # Создаем фоновую задачу для выполнения операции
    async def execute_operation():
        return operations[operator](x, y)

    # Запускаем фоновую задачу
    task = asyncio.create_task(execute_operation())

    # Сохраняем задачу в словаре
    background_tasks[task_id] = task

    return {"task_id": task_id}


@app.get("/status/{task_id}")
async def status(task_id: int):
    # Проверяем, существует ли задача с заданным идентификатором
    if task_id not in background_tasks:
        return {"error": "Задача не найдена"}

    task = background_tasks[task_id]

    # Проверяем статус выполнения задачи
    if task.done():
        # Получаем результат выполнения задачи
        result = task.result()

        # Удаляем задачу из словаря
        del background_tasks[task_id]

        return {"status": "Задача выполнена", "result": result}
    else:
        return {"status": "Задача выполняется"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)