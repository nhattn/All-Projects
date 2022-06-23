package vn.corenlp.chunker;

import java.io.FileInputStream;
import java.io.InputStream;

import opennlp.tools.chunker.ChunkerME;
import opennlp.tools.chunker.ChunkerModel;

import org.apache.log4j.Logger;

import java.io.File;
import java.io.IOException;

import java.util.List;
import java.util.ArrayList;

public class PosChunker {
    private static PosChunker posChunker = null;
    private ChunkerME chunker;
    public final static Logger LOGGER = Logger.getLogger(PosChunker.class);
    public PosChunker() throws IOException {
        LOGGER.info("Loading POS Chunking model");
        String modelPath = System.getProperty("user.dir") + "/models/poschunker/vi-chunk";
        if (!new File(modelPath).exists()) throw new IOException("PosTagger: " + modelPath + " is not found!");
        InputStream inChunk = new FileInputStream(modelPath);
        ChunkerModel chunkModel = new ChunkerModel(inChunk);
        chunker = new ChunkerME(chunkModel);
    }
    public static PosChunker initialize() throws IOException {
        if (posChunker == null) {
            posChunker = new PosChunker();
        }
        return posChunker;
    }
    public List<String> chunking(String[] tokens, String[] postags) throws IOException {
        List<String> output = new ArrayList<>();
        if (tokens.length == 0 || tokens.length != postags.length) {
            return output;
        }
        String[] chunktags = chunker.chunk(tokens, postags);
        for (int i = 0; i < tokens.length; i++) {
            output.add(chunktags[i]);
        }
        return output;
    }
}
