function loadData(dataSet) {
    // TODO: This needs to be made modular to account for different input feature sizes.
    // Based on https://codelabs.developers.google.com/codelabs/tfjs-training-regression/index.html#4
    return tf.tidy(() => {
        tf.util.shuffle(dataSet);
        const inOut = dataSet.map(student => ({
            time_taken: student.time_taken,
            average_time_between_questions: student.average_time_between_questions,
            page_leaves: student.page_leaves,
        }));

        const tensorInOut = inOut.map(student => [student.time_taken, student.average_time_between_questions, student.page_leaves]);
        console.log(inOut);
        const inOutTensor = tf.tensor2d(tensorInOut, [dataSet.length, 3]);

       return inOutTensor;
    });
}

let iterations = parseInt(window.localStorage.getItem("autoencoder_iterations"));
intervalTracker = {};
function loadModel(dataSet) {
    const data = loadData(dataSet);
    const featureSize = 3;
    const layer1 = 10;
    const layer2 = 5;
    const layer3 = 2;


    const inputs = tf.input({shape: [featureSize]});
    const encodeLayer1 = tf.layers.dense({units: layer1, activation: "tanh"});
    const encodeLayer2 = tf.layers.dense({units: layer2, activation: "tanh"});
    const encodeLayer3 = tf.layers.dense({units: layer3, activation: "tanh"});
    const encodeOutput = encodeLayer3.apply(encodeLayer2.apply(encodeLayer1.apply(inputs)));


    const decodeInputs = tf.input({shape: [layer3]});
    const decodeLayer1 = tf.layers.dense({units: layer2, activation: "tanh"});
    const decodeLayer2 = tf.layers.dense({units: layer1, activation: "tanh"});
    const decodeLayer3 = tf.layers.dense({units: featureSize, activation: "linear"});
    const decodeOutput = decodeLayer3.apply(decodeLayer2.apply(decodeLayer1.apply(decodeInputs)));

    const encoder = tf.model({
        inputs: inputs,
        outputs: encodeOutput
    });
    const decoder = tf.model({
        inputs: decodeInputs,
        outputs: decodeOutput
    });
    const model = {encoder: encoder, decoder: decoder};


    const loss = (input, output) => {
            return input.sub(output).square().mean()
    };

    const calcLoss = () => tf.tidy(() => {
            let calcedLoss =  loss(model.decoder.predict(model.encoder.predict(data)), data);
            return calcedLoss;
    });

    const optimizer = tf.train.adam(.08);
    intervalTracker.autoencoder = setInterval(trainModel, 1);
    function trainModel() {
        if (iterations === 0) {
            clearInterval(intervalTracker.autoencoder);
            document.getElementById("autoencoder-iterations-display").innerText = iterations;
            predict();
        }
        else {
            console.log(tf.memory());
            const printLoss = calcLoss();
            document.getElementById("loss").innerText = printLoss.dataSync()[0];
            printLoss.dispose();
            optimizer.minimize(calcLoss);
            iterations -= 1;
            document.getElementById("autoencoder-iterations-display").innerText = iterations;
        }
    }

    function predict() {
        let predictions = decoder.predict(encoder.predict(data));
        let indivError = predictions.sub(data).mean(1);
        let averageError = calcLoss(predictions, data).sqrt();
        let errorsCond = indivError.greaterEqual(averageError);
        let predictionsJS = predictions.arraySync(); 
        let errorsCondJS = errorsCond.dataSync(); 
        errorsCond.dispose(); 
        predictions.dispose(); 
        indivError.dispose(); 
        averageError.dispose(); 
        
        let anomalies = [];
        for (let i = 0; i < errorsCondJS.length; i++) {
            if (errorsCondJS[i]) {
                anomalies.push(predictionsJS[i]);
            }
        }

        kmeans(anomalies);
    }

    function kmeans(anomalies) {
        console.log(anomalies);
        console.log("I got here");
    }
}







