from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# 火山引擎API配置
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY", "fe77ab7f-84af-47c9-9885-c8ecac7684c5")
VOLCANO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"


def translate_with_volcano(text: str, source_lang: str = "ja", target_lang: str = "zh") -> Optional[str]:
    """
    使用火山引擎翻译API进行翻译
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言代码 (ja=日语, zh=中文, en=英语)
        target_lang: 目标语言代码
    
    Returns:
        翻译后的文本，如果失败则返回None
    """
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer fe77ab7f-84af-47c9-9885-c8ecac7684c5",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "doubao-seed-translation-250915",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text,
                            "translation_options": {
                                "source_language": source_lang,
                                "target_language": target_lang
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(VOLCANO_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"翻译API响应: {result}")
        
        # 解析火山引擎的响应格式: output[0].content[0].text
        try:
            translated_text = result.get("output", [{}])[0].get("content", [{}])[0].get("text", "").strip()
            
            if translated_text:
                logger.info(f"翻译成功: {text} -> {translated_text}")
                return translated_text
            else:
                logger.warning(f"翻译返回空结果: {text}")
                return None
        except (IndexError, KeyError) as e:
            logger.error(f"解析翻译响应失败: {result}, 错误: {e}")
            return None
            
    except Exception as e:
        logger.error(f"翻译失败: {text}, 错误: {e}")
        return None


def translate_product_name(product_name: str) -> Optional[str]:
    """
    翻译产品名称从日文到中文
    使用火山引擎翻译API进行翻译
    
    返回: 中文翻译，如果失败则返回None
    """
    if not product_name:
        return None
    
    # 尝试使用API翻译 (ja=日语, zh=中文)
    translated = translate_with_volcano(product_name, source_lang="ja", target_lang="zh")
    
    if translated:
        return translated
    
    # API失败时使用手动映射表（降级方案）
    # translation_map = {
    #     "GQuuuuuuX": "GX",
    #     "エンディミオン": "安迪米昂",
    #     "ユニット": "单元",
    #     "覚醒時": "觉醒时",
    #     "ストライクフリーダム": "强袭自由",
    #     "ガンダム": "高达",
    #     "HG": "HG",
    #     "MG": "MG",
    #     "RG": "RG",
    #     "PG": "PG",
    #     "メカニカルクリア": "机械透明",
    # }
    
    # result = product_name
    # for jp, cn in translation_map.items():
    #     result = result.replace(jp, cn)
    
    # # 如果翻译后的结果与原文件相同，说明没有翻译，返回None
    # if result == product_name:
    #     logger.warning(f"未找到翻译: {product_name}")
    #     return None
    
    return None
