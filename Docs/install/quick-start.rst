.. _install-quick-start:

###########
Quick Start
###########

This page describes how to quickly install the latest version of AIMET for PyTorch framework.

For all the framework variants and compute platform, see :ref:`Installation <install-index>`.

Installation
============

Type the following command to install AIMET for PyTorch framework using pip package manager.

.. code-block:: bash

    python3 -m pip install aimet-torch

AIMET PyTorch package has been tested using the following recommended host platform configuration:

* 64-bit Intel x86-compatible processor
* Python 3.8–3.12
* Ubuntu 22.04
* For GPU variants:
    * Nvidia GPU card (Compute capability 5.2 or later)
    * Nvidia driver version 455 or later (using the latest driver is recommended; both CUDA and cuDNN are supported)

Verification
============

To confirm that AIMET PyTorch is installed correctly, you can verify the installation by executing the
following sample code snippet.

.. code-block:: python

    import torch
    x = torch.randn(100)


Then instantiate 8-bit symmetric affine quantizer.

.. code-block:: python

    import aimet_torch.quantization as Q
    scale = torch.ones(()) / 100
    offset = torch.zeros(())
    out = Q.affine.quantize(x, scale, offset, qmin=-128, qmax=127)
    print(out)

The quantized output should be something similar to the one shown below.

.. rst-class:: script-output

    .. code-block:: none

        tensor([  80.,  119.,   63.,  127.,  127.,   64., -128.,  -43.,  127.,  -90.,
                  66.,   26.,  127.,   56.,   89., -128.,  -48., -105.,   10.,   78.,
                 -69.,  -65., -128.,   18.,  127.,  121., -128., -116.,  -99.,   30.,
                 -83.,  -59., -128.,  127., -104.,  127.,   50.,  -59.,   59.,   -2.,
                   4.,  -79.,   42.,   12., -100.,   55.,  -48.,   13.,   63.,  -52.,
                  31.,  -33.,  -85.,  -96.,  127., -128.,  -75.,   90., -128.,  -12.,
                  72.,  -89.,  127.,  -49.,   81.,   35., -102., -128.,    2.,  127.,
                 -86., -128.,   93.,  -77.,  127., -128.,   -2., -128.,   12., -105.,
                -116., -128.,   42.,  -64.,  -58.,  -88.,  -72.,  127.,  -35.,   68.,
                 -63.,  -28.,   14.,   -1., -128.,  -27.,  -91.,  -77.,   56.,  127.])

Quick example
=============

Next, using :mod:`aimet_torch` for the MobileNetV2 network, create a :class:`QuantizationSimModel`, perform calibration,
and then evaluate it:

**Step 1**: Let's handle necessary imports and other setup.

.. literalinclude:: ../snippets/torch/installation_verification.py
            :language: python
            :start-after: # [step_1]
            :end-before: # End of [step_1]

**Step 2**: We will create :class:`QuantizationSimModel` and ensure the model contains quantization operations.

.. literalinclude:: ../snippets/torch/installation_verification.py
            :language: python
            :start-after: # [step_2]
            :end-before: # End of [step_2]

The model should be composed of Quantized :class:`nn.Modules`, similar to the output shown below:

.. rst-class:: script-output

    .. code-block:: none
   
        MobileNetV2(
        (features): Sequential(
        (0): Conv2dNormActivation(
          (0): QuantizedConv2d(
            3, 32, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False
            (param_quantizers): ModuleDict(
              (weight): QuantizeDequantize(shape=(32, 1, 1, 1), qmin=-128, qmax=127, symmetric=True)
            )
            (input_quantizers): ModuleList(
              (0): QuantizeDequantize(shape=(), qmin=0, qmax=65535, symmetric=False)
            )
            (output_quantizers): ModuleList(
              (0): None
            )
          )
        )
        ...
        )

**Step 3**: We perform calibration. As a proof of concept, random input is being passed in. However, calibration should be performed using a representative dataset in real world cases.

.. literalinclude:: ../snippets/torch/installation_verification.py
            :language: python
            :start-after: # [step_3]
            :end-before: # End of [step_3]

**Step 4**: We perform evaluation.

.. literalinclude:: ../snippets/torch/installation_verification.py
            :language: python
            :start-after: [step_4]
            :end-before: # End of [step_4]

The output generated should be of type :class:`DequantizedTensor` and similar to the one shown below.

.. rst-class:: script-output

    .. code-block:: none

        DequantizedTensor([[-1.7466,  0.8405,  1.8606,  ..., -0.9714,  0.8366, 2.2363],
                           [-1.6091,  1.0449,  1.7788,  ..., -0.9904,  1.0861, 2.2431],
                           [-1.5307,  0.8442,  1.5157,  ..., -0.7793,  0.6327, 2.3861],
                           ...,
                           [-1.3610,  1.4499,  2.2068,  ..., -0.8188,  1.1155, 2.5962],
                           [-1.1619,  1.2217,  2.1050,  ..., -0.5301,  0.9150, 2.1458],
                           [-1.6340,  0.9826,  2.2459,  ..., -1.0769,  0.9054, 2.2315]],
                           device='cuda:0', grad_fn=<AliasBackward0>)
