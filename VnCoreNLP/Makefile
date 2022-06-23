JAR_FILE = VnCoreNLP-1.1.1.jar

release:
ifeq ($(shell test -e $(JAR_FILE) && echo -n yes),yes)
	docker stop vncorenlp
	docker rm vncorenlp
	docker build --no-cache -t vncorenlp:latest -f Dockerfile .
else
	@echo "File not exists"
endif

build:
	docker build -t vncorenlp:build -f Build .
	docker create --name extract vncorenlp:build
	docker cp extract:/target/VnCoreNLP-1.1.1.jar ./VnCoreNLP-1.1.1.jar
	docker rm -f extract

run:
	docker run --name vncorenlp -p 8090:8080 -d vncorenlp:latest
