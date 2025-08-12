import requests, json, io, logging
from BaseSettings.config import config
from PIL import Image

logger = logging.getLogger(__name__)

# Neural networks class
class neural_networks:
    
#Protected
    def _FLUX_request(self, model: str, prompt: str, size: list[int, int], seed: int, num_inference_steps: int, 
                     provider: str = "hf") -> Image.Image|None:

        model_url = config.flux_models.get(model)
        if not model_url:
            logger.error(f"Неизвестная модель FLUX: {model}")
            return None
            
        payload = {
            "inputs": prompt,
            "parameters": {
                "guidance_scale": 1.5,
                "num_inference_steps": num_inference_steps,
                "width": size[0],
                "height": size[1],
                "seed": seed
            }
        }
        
        if provider == "hf":
            # Используем HuggingFace Inference API
            for i in range(6):
                try:
                    response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model_url}",
                        headers={"Authorization": "Bearer " + config.hf_tokens[i], 
                                "Content-Type": "application/json"},
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        try:
                            # Проверяем, что ответ действительно является изображением
                            content_type = response.headers.get('content-type', '')
                            if not content_type.startswith('image/'):
                                logger.error(f"FLUX {model} API вернул неверный тип контента: {content_type}")
                                continue
                                
                            image = Image.open(io.BytesIO(response.content))
                            logger.info(f"FLUX {model} API request был успешен, статус: {response.status_code}")
                            return image
                        except Exception as e:
                            logger.error(f"FLUX {model} ошибка при обработке изображения: {str(e)}")
                            continue
                    else:
                        logger.error(f"FLUX {model} API ошибка, статус: {response.status_code}, ответ: {response.content}")
                except Exception as e:
                    logger.error(f"FLUX {model} ошибка запроса: {str(e)}")
                    
        elif provider == "fal":
            # TODO: Добавить поддержку FAL.ai провайдера для других моделей
            logger.error("FAL.ai провайдер пока не реализован")
            return None
            
        return None
    
    def _mistral_large_text(self, prompt: list[dict[str, str]], temperature: float, top_p: float) -> tuple[str, int, int]|str:
        """Метод для генерации текста с помощью Mistral Large"""
        data = {
            "messages": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": 1024,
            "model": "mistral-large-latest"
        }
        try:
            response = requests.post("https://api.mistral.ai/v1/chat/completions",
                                  headers={"Content-Type": "application/json", "Authorization": "Bearer "+ config.mistral_token},
                                  json=data)
            if response.status_code == 200:
                logger.info(f"Mistral text generation was successful, status code: {response.status_code}")
                response = json.loads(response.text)
                return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
            else:
                logger.error(f"Mistral text generation error, status code: {response.status_code}, response text: {response.content}")
                return "Извините, сервис временно недоступен. Попробуйте повторить запрос позже.", 0, 0
        except Exception as e:
            logger.error(f"Mistral text generation exception: {str(e)}")
            return "Произошла ошибка при генерации текста. Пожалуйста, попробуйте позже.", 0, 0

    def _mistral_vision(self, prompt: list[dict[str, str]], temperature: float, top_p: float) -> tuple[str, int, int]|str:
        """Метод для обработки запросов с изображениями с помощью Mistral Vision"""
        data = {
            "messages": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": 1024,
            "model": "pixtral-12b-latest"
        }
        try:
            response = requests.post("https://api.mistral.ai/v1/chat/completions",
                                  headers={"Content-Type": "application/json", "Authorization": "Bearer "+ config.mistral_token},
                                  json=data)
            if response.status_code == 200:
                logger.info(f"Mistral vision request was successful, status code: {response.status_code}")
                response = json.loads(response.text)
                return response["choices"][0]["message"]["content"], response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"]
            else:
                logger.error(f"Mistral vision request error, status code: {response.status_code}, response text: {response.content}")
                return "Извините, сервис обработки изображений временно недоступен. Попробуйте повторить запрос позже.", 0, 0
        except Exception as e:
            logger.error(f"Mistral vision request exception: {str(e)}")
            return "Произошла ошибка при обработке изображения. Пожалуйста, попробуйте позже.", 0, 0

    def generate_image(self, user_data: dict, prompt: str, size: list[int, int], seed: int, 
                      num_inference_steps: int = 30) -> tuple[Image.Image|None, str]:

        # Определяем тариф и доступные модели
        if user_data['ultra']:
            tariff = "ultra"
        elif user_data['pro']:
            tariff = "pro"
        elif user_data['basic']:
            tariff = "basic"
        else:
            tariff = "free"
            
        # Проверяем лимиты
        if tariff == "free" and user_data['image_requests'] >= config.free_image_limit:
            return None, "Достигнут дневной лимит генераций для бесплатного тарифа"
        elif tariff == "basic" and user_data['image_requests'] >= 3:
            return None, "Достигнут дневной лимит генераций для тарифа BASIC"
        elif tariff == "pro" and user_data['image_requests'] >= config.pro_image_limit:
            return None, "Достигнут дневной лимит генераций для тарифа PRO"
            
        # Получаем настройки изображения
        settings = user_data.get('images', '').split('|')
        selected_model = settings[2] if len(settings) > 2 else 'schnell'
        
        # Проверяем, доступна ли выбранная модель для данного тарифа
        available_models = config.tariff_models[tariff]
        if selected_model not in available_models:
            selected_model = available_models[0]  # Используем первую доступную модель
            
        # Логируем попытку генерации
        logger.info(f"Попытка генерации изображения. Тариф: {tariff}, модель: {selected_model}")
        
        # Пробуем сгенерировать изображение выбранной моделью
        image = self._FLUX_request(selected_model, prompt, size, seed, num_inference_steps)
        if image:
            logger.info(f"Успешная генерация изображения моделью {selected_model}")
            return image, ""
            
        # Если не получилось, пробуем другие доступные модели
        logger.info(f"Не удалось сгенерировать изображение моделью {selected_model}, пробуем альтернативные модели")
        for model in available_models:
            if model != selected_model:
                logger.info(f"Пробуем модель {model}")
                image = self._FLUX_request(model, prompt, size, seed, num_inference_steps)
                if image:
                    logger.info(f"Успешная генерация изображения альтернативной моделью {model}")
                    return image, ""
                    
        logger.error(f"Не удалось сгенерировать изображение ни одной из доступных моделей для тарифа {tariff}")
        return None, "Не удалось сгенерировать изображение. Попробуйте другую модель или повторите позже"