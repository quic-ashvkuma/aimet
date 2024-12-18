# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2022, 2024, Qualcomm Innovation Center, Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
#  SPDX-License-Identifier: BSD-3-Clause
#
#  @@-COPYRIGHT-END-@@
# =============================================================================
# pylint: skip-file
from tensorflow.keras import losses, metrics, optimizers, preprocessing
# End of imports

# Load the model
from tensorflow.keras import applications

model = applications.MobileNetV2()
# End of loading model

# Fold batch norm
from aimet_tensorflow.keras.batch_norm_fold import fold_all_batch_norms

_, model = fold_all_batch_norms(model)
# End of folding batch norm

# Set up dataset
from tensorflow.keras.applications import mobilenet_v2

BATCH_SIZE = 32
imagenet_dataset = preprocessing.image_dataset_from_directory(
    directory='<your_imagenet_validation_data_path>',
    label_mode='categorical',
    image_size=(224, 224),
    batch_size=BATCH_SIZE,
    shuffle=True,
)

imagenet_dataset = imagenet_dataset.map(
    lambda x, y: (mobilenet_v2.preprocess_input(x), y)
)

NUM_CALIBRATION_SAMPLES = 1024
calibration_dataset = imagenet_dataset.take(NUM_CALIBRATION_SAMPLES // BATCH_SIZE)
eval_dataset = imagenet_dataset.skip(NUM_CALIBRATION_SAMPLES // BATCH_SIZE)
# End of dataset

# Create QuantSim object
from aimet_common.defs import QuantScheme
from aimet_common.quantsim_config.utils import get_path_for_per_channel_config
from aimet_tensorflow.keras.quantsim import QuantizationSimModel

PARAM_BITWIDTH = 8
ACTIVATION_BITWIDTH = 16
sim = QuantizationSimModel(
    model,
    quant_scheme=QuantScheme.training_range_learning_with_tf_init,
    default_param_bw=PARAM_BITWIDTH,
    default_output_bw=ACTIVATION_BITWIDTH,
    config_file=get_path_for_per_channel_config(),
)
# End of creating QuantSim object


def pass_calibration_data(model, _):
    for inputs, _ in calibration_dataset:
        _ = model(inputs)


# Compute quantization encodings
sim.compute_encodings(pass_calibration_data, None)

sim.model.compile(
    optimizer=optimizers.SGD(1e-6),
    loss=[losses.CategoricalCrossentropy()],
    metrics=[metrics.CategoricalAccuracy()],
)
# End of computing quantization encodings

# Export the model
_, accuracy = sim.model.evaluate(eval_dataset)
print(f'Quantized accuracy (W{PARAM_BITWIDTH}A{ACTIVATION_BITWIDTH}): {accuracy:.4f}')

sim.export(path='/tmp', filename_prefix='quantized_mobilenet_v2')
# End of exporting the model

# Perform QAT
sim.model.fit(calibration_dataset, epochs=10)

_, accuracy = sim.model.evaluate(eval_dataset)
print(f'Model accuracy after QAT: {accuracy:.4f}')
# End of QAT