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

        const tensorInOut = inOut.map(student => [student.time_taken, student.average_time_between_questions, student.page_leaves]);
        console.log(inOut);
        const inOutTensor = tf.tensor2d(tensorInOut, [data.length, 3]);

        return {
            inputs: inOutTensor,
            inOutMax: 0,
            inOutMin: 1
        }
    })
}


async function loadModel(dataSet) {
    console.log(dataSet);
    const data = loadData(dataSet);
    const model = createModel(4, 10, 5, 2);
    await trainModel(model, data);
    data["inputs"].print();
}

function createModel(feature_count, layer_1, layer_2, layer_3) {
    let model = tf.sequential();
    model.add(tf.layers.dense({inputShape: [feature_count], units: layer_1, useBias: true}));
    model.add(tf.layers.dense({units: layer_2, useBias: true}));
    model.add(tf.layers.dense({units: layer_3, useBias: true}));
    model.add(tf.layers.dense({units: layer_2, useBias: true}));
    model.add(tf.layers.dense({units: layer_1, useBias: true}));
    model.add(tf.layers.dense({units: feature_count}));
    return model
}

async function trainModel(model, inputs) {
    model.compile({
        optimizer: tf.train.adam(),
        loss: tf.losses.meanSquaredError,
        metrics: ['mse']
    });

    const batchSize = 28;
    const epochs = 50;

    return await model.fit(inputs, inputs, {
        batchSize,
        epochs,
        shuffle: true,
        callbacks: function() {
            console.log("I trained the model!");
        }
    })

}

createModel(4, 10, 10, 10);



