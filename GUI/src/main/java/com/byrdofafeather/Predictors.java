package com.byrdofafeather;

import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;

public class Predictors {
}

class AutoEncoder {
	INDArray dataSet;
	AutoEncoder(INDArray dataSet) {
		dataSet = scaleData();

	}

	INDArray scaleData(){
		float[] size = new float[1];
		int[] features = new int[1];
		INDArray scaledData = new Nd4j().create(size, features, 'c');
		return scaledData;
	}

	void run(){

	}
}