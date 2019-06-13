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
    const model = createModel(4, 10, 5, 2, data);
    await trainModel(model, data);
    data["inputs"].print();
}

function createModel(featureSize, layer1, layer2, layer3) {
    const inputs = tf.input({shape: [featureSize]});
    const encodeLayer1 = tf.layers.dense({units: layer1, activation: "tanh"});
    const encodeLayer2 = tf.layers.dense({units: layer2, activation: "tanh"});
    const encodeLayer3 = tf.layers.dense({units: layer3, activation: "tanh"});
    const decodeLayer1 = tf.layers.dense({units: layer2, activation: "tanh"});
    const decodeLayer2 = tf.layers.dense({units: layer1, activation: "tanh"});
    const decodeLayer3 = tf.layers.dense({units: featureSize, activation: "linear"});
    const output =
        decodeLayer3.apply(
            decodeLayer2.apply(
                decodeLayer1.apply(
                    encodeLayer3.apply(
                        encodeLayer2.apply(
                            encodeLayer1.apply(
                                inputs
                            )
                        )
                    )
                )
            )
        );
    return tf.model({inputs: inputs, outputs: output})
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



