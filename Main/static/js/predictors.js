function loadData(data) {
    // TODO: This needs to be made modular to account for different input feature sizes.
    // Based on https://codelabs.developers.google.com/codelabs/tfjs-training-regression/index.html#4
    return tf.tidy(() => {
        tf.util.shuffle(data);
        const inOut = data.map(student => ({
            time_taken: student.time_taken,
            average_time_between_questions: student.average_time_between_questions,
            page_leaves: student.page_leaves,
        }));

        const inOutTensor = tf.tensor2d(inOut, [inOut.length, 1]);

        const inOutMax = inOutTensor.max();
        const inOutMin = inOutTensor.min();

        const normalizedInOut = inOutTensor.sub(inOutMin).div(inOutMax.sub(inOutMax));
        return {
            inputs: normalizedInOut,
            inOutMax: inOutMax,
            inOutMin: inOutMin
        }
    })
}


function loadModel(dataSet) {
    const data = loadData(dataSet);
    const model = createModel(4, 10, 5, 2);
}

function createModel(feature_count, layer_1, layer_2, layer_3) {
    let model = tf.sequential();
    model.add(tf.layers.dense({inputShape: [feature_count], units: layer_1, useBias: true}));
    model.add(tf.layers.dense({units: layer_2, useBias: true}));
    model.add(tf.layers.dense({units: layer_3, useBias: true}));
    model.add(tf.layers.dense({units: layer_2, useBias: true}));
    model.add(tf.layers.dense({units: layer_1, useBias: true}));
    model.add(tf.layers.dense({units: feature_count, useBias: true}));
    return model
}

createModel(4, 10, 10, 10);



