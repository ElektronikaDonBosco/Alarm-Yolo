# Object detection

En este documento se analizaran las diferentes maneras que existen para hacer el proceso de deteccion de objetos en imagenes.

## Modelos para la detección de objetos

### Redes convolucionales

Los modelos para la detección de objetos mediante convoluciones se dividen en dos tipos: los de una etapa o los de dos etapas. Esta diferencia se hace porque unos de los modelos utilizan las regiones de interés (Region of interest o RoI) para realizar las detecciones y los otros dividen la imagen en cuadrados simétricos en vez de utilizar RoI.

* Modelo de una etapa:Los modelos de una etapa eliminan el proceso de extracción de las regiones de interés y clasifican y hacen
  retroceder directamente las cajas de anclaje candidatas. Algunos ejemplos son: la familia YOLO (YOLOv2, YOLOv3, YOLOv4 y YOLOv5), Single-Shot Detector (SSD), CornerNet y CenterNet.
  YOLO es una arquitectura para la detección de objetos en imágenes. Utiliza una única red neuronal convolucional y a partir de una imagen utilizada como entrada, predice simultáneamente múltiples bounding boxes, las etiquetas de las clases a detectar en la imagen y la probabilidad de cada una de ellas. Su entrenamiento se realiza utilizando aprendizaje supervisado. 
* Modelo de dos etapas: Los modelos de dos etapas Dividen la tarea de detección de objetos en dos etapas: primero extraen las regiones de interés, para después clasificar y analizar esas regiones. Algunos ejemplos de arquitecturas de detección de objetos que están orientadas a 2 etapas son R-CNN, Fast-RCNN, Faster-RCNN y Mask-RCNN.

[Mas info](https://neptune.ai/blog/object-detection-algorithms-and-libraries)

### Transformers

También existen nuevos modos para la detección de objetos en los que se usan Transformers, inicialmente utilizados para modelos de lenguaje natural llamados NLP models. Los [transformers](https://arxiv.org/abs/1706.03762) utilizados para crear los Large Language Models (LLMs) son sistemas para poder medir una secuencia de datos sin perder información al procesar estas. Para ello se vectorizan los textos utilizando text-embeddings para sacar tokens o imágenes utilizando encoders. Después de este proceso los vectores no tienen tanto volumen y de esta manera estos vectores son más fáciles de procesar.

Durante el año 2022 han surgido avances que han llevado estos modelos a entornos de visión, llamados Vision Transformers ViT. En estos links [1](https://github.com/lucidrains/vit-pytorch#research-ideas), [2](https://github.com/taki0112/vit-tensorflow) y [3](https://github.com/hustvl/YOLOShttps://huggingface.co/docs/transformers/main/en/model_doc/yolo) hay diferentes ejemplos con los modelos creados y listos para entrenar, pero solo para clasificación. Habría que modificarlos para su uso en detección de objetos o utilizar los ejemplos creados en [keras](https://keras.io/examples/vision/object_detection_using_vision_transformer/), [facebook](https://github.com/facebookresearch/detr) o [google](https://github.com/google-research/vision_transformer).

[Mas info](https://viso.ai/deep-learning/vision-transformer-vit/)

Guia paso por paso: paso [1](https://learnopencv.com/attention-mechanism-in-transformer-neural-networks/) y paso [2](https://learnopencv.com/the-future-of-image-recognition-is-here-pytorch-vision-transformer/).
