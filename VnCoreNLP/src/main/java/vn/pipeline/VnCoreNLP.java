package vn.pipeline;

import vn.corenlp.ner.NerRecognizer;
import vn.corenlp.parser.DependencyParser;
import vn.corenlp.postagger.PosTagger;
import vn.corenlp.tokenizer.Tokenizer;
import vn.corenlp.chunker.PosChunker;
import vn.corenlp.wordsegmenter.WordSegmenter;

import java.io.*;
import java.lang.Thread;
import java.lang.Runnable;
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.URLDecoder;

import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

public class VnCoreNLP {
    public static DependencyParser dependencyParser = null;
    public static NerRecognizer nerRecognizer = null;
    public static PosTagger posTagger = null;
    public static PosChunker posChunker = null;
    public static WordSegmenter wordSegmenter = null;

    public static void kernelInit() {
        try {
            dependencyParser = DependencyParser.initialize();
            nerRecognizer = NerRecognizer.initialize();
            posTagger = PosTagger.initialize();
            posChunker = PosChunker.initialize();
            wordSegmenter = WordSegmenter.initialize();
        } catch(IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException {
        (new Thread(new Runnable() {
            @Override
            public void run() {
                kernelInit();
            }
        })).start();
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/", new HttpHandler() {
            @Override
            public void handle(final HttpExchange exchange) throws IOException {
                Headers responseHeaders = exchange.getResponseHeaders();
                responseHeaders.set("Content-Type", "application/json");
                OutputStream resp = exchange.getResponseBody();
                String hithere = "[\"Hi there !\"]";
                final byte[] responseAsBytes = hithere.getBytes("UTF-8");
                exchange.sendResponseHeaders(200, responseAsBytes.length);
                resp.write(responseAsBytes);
                resp.flush();
                resp.close();
            }
        });
        server.createContext("/api/nlp", new HttpHandler() {
            @Override
            public void handle(final HttpExchange exchange) throws IOException {
                String requestMethod = exchange.getRequestMethod();
                Headers responseHeaders = exchange.getResponseHeaders();
                OutputStream resp = exchange.getResponseBody();
                responseHeaders.set("Content-Type", "application/json");
                if (dependencyParser == null || nerRecognizer == null || posTagger == null || posChunker == null || wordSegmenter == null) {
                    String respText = "{\"error\":\"kernel is not ready\"}";
                    final byte[] responseAsBytes = respText.getBytes("UTF-8");
                    exchange.sendResponseHeaders(200, responseAsBytes.length);
                    resp.write(responseAsBytes);
                    resp.flush();
                    resp.close();
                    exchange.close();
                    return;
                }
                if(requestMethod.equalsIgnoreCase("POST")) {
                    byte[] buffer = new byte[4096];
                    int bytesRead = 0;
                    StringBuilder query = new StringBuilder();
                    InputStream is = exchange.getRequestBody();
                    while ((bytesRead = is.read(buffer)) != -1) {
                        query.append(new String(buffer, 0, bytesRead));
                    }
                    is.close();
                    Map<String, Object> params = parseQuery(query.toString());
                    String text = params.getOrDefault("text", "").toString();
                    String respText = "{\"error\":\"Invalid params\"}";
                    if (text == null || "".equals(text)) {
                        respText = "{\"error\":\"Text is empty\"}";
                        final byte[] responseAsBytes = respText.getBytes("UTF-8");
                        exchange.sendResponseHeaders(400, responseAsBytes.length);
                        resp.write(responseAsBytes);
                        resp.flush();
                        resp.close();
                    } else {
                        try {
                            Annotation annotation = new Annotation(text);

                            List<String> rawSentences = Tokenizer.joinSentences(Tokenizer.tokenize(annotation.getRawText()));
                            annotation.setSentences(new ArrayList<>());

                            for (String rawSentence : rawSentences) {
                                if (rawSentence.trim().length() > 0) {
                                    Sentence sentence = new Sentence(rawSentence, wordSegmenter, posTagger, nerRecognizer, dependencyParser);
                                    annotation.getSentences().add(sentence);
                                    annotation.getTokens().addAll(sentence.getTokens());
                                    annotation.getWords().addAll(sentence.getWords());
                                    annotation.setWordSegmentedText(annotation.getWordSegmentedTaggedText() + sentence.getWordSegmentedSentence() + " ");
                                }
                            }

                            annotation.setWordSegmentedText(annotation.getWordSegmentedTaggedText().trim());

                            List<Sentence> sentences = annotation.getSentences();

                            StringBuffer jsb = new StringBuffer();
                            jsb.append("[");
                            for (int i = 0; i < sentences.size(); i++) {
                                Sentence sent = sentences.get(i);
                                List<Word> words = sent.getWords();
                                List<String> tokens = new ArrayList<>();
                                List<String> postags = new ArrayList<>();
                                for (int j = 0; j < words.size(); j++) {
                                    tokens.add(words.get(j).getForm());
                                    String wtag = words.get(j).getPosTag();
                                    if (wtag == null) {
                                        wtag = "X";
                                    }
                                    postags.add(wtag);
                                }
                                List<String> chunktags = posChunker.chunking(tokens.toArray(new String[tokens.size()]), postags.toArray(new String[postags.size()]));
                                jsb.append("[");
                                for (int j = 0; j < words.size(); j++) {
                                    String word = words.get(j).getForm().replace("\"", "\\\"");
                                    String tag = words.get(j).getPosTag();
                                    String chunk = chunktags.get(j);
                                    String ner = words.get(j).getNerLabel();
                                    if (tag == null) {
                                        tag = "X";
                                    }
                                    if (chunk == null) {
                                        chunk = "O";
                                    }
                                    if (ner == null) {
                                        ner = "O";
                                    }
                                    jsb.append("[");
                                    jsb.append("\"" + word + "\",");
                                    jsb.append("\"" + tag + "\",");
                                    jsb.append("\"" + chunk + "\",");
                                    jsb.append("\"" + ner + "\"");
                                    jsb.append("]");
                                    if (j < words.size() - 1) {
                                        jsb.append(",");
                                    }
                                }
                                jsb.append("]");
                                if (i < sentences.size() - 1) {
                                    jsb.append(",");
                                }
                            }
                            jsb.append("]");
                            respText = jsb.toString();
                            final byte[] responseAsBytes = respText.getBytes("UTF-8");
                            exchange.sendResponseHeaders(200, responseAsBytes.length);
                            resp.write(responseAsBytes);
                            resp.flush();
                            resp.close();
                        } catch (Exception e) {
                            throw e;
                        }
                    }
                } else {
                    String badRequest = "{\"error\":\"400 : Bad request !!!\"}";
                    exchange.sendResponseHeaders(400, badRequest.length());
                    resp.write(badRequest.getBytes("UTF-8"));
                    resp.flush();
                    resp.close();
                }
                exchange.close();
            }
        });
        server.setExecutor(null);
        server.start();
    }
    public static Map<String, Object> parseQuery(String query) throws UnsupportedEncodingException {
        Map<String, Object> parameters = new HashMap<String, Object>();
        if (query == null || "".equals(query)) {
            return parameters;
        }
        String pairs[] = query.split("[&]");
        for (String pair : pairs) {
            String param[] = pair.split("[=]");
            String key = null;
            String value = null;
            if (param.length > 0) {
                key = URLDecoder.decode(param[0], "UTF-8");
            }
            if (param.length > 1) {
                value = URLDecoder.decode(param[1], "UTF-8");
            }
            if (parameters.containsKey(key)) {
                Object obj = parameters.get(key);
                if(obj instanceof List<?>) {
                    List<String> values = (List<String>)obj;
                    values.add(value);
                } else if(obj instanceof String) {
                    List<String> values = new ArrayList<String>();
                    values.add((String)obj);
                    values.add(value);
                    parameters.put(key, values);
                }
            } else {
                parameters.put(key, value);
            }
        }
        return parameters;
    }
}
