FROM openjdk:8-jre-alpine

WORKDIR /home/app

# copy jar
COPY ./VnCoreNLP-1.1.1.jar ./VnCoreNLP.jar
COPY ./models ./models

# run jar
CMD ["java", "-Xmx2g", "-jar", "VnCoreNLP.jar"]
