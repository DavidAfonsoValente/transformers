# coding=utf-8
# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest

from transformers import is_torch_available
from transformers.testing_utils import require_sentencepiece, require_tokenizers, require_torch, slow, require_flash_attn


if is_torch_available():
    import torch

    from transformers import XLMRobertaModel


@require_sentencepiece
@require_tokenizers
@require_torch
class XLMRobertaModelIntegrationTest(unittest.TestCase):
    @slow
    def test_xlm_roberta_base(self):
        model = XLMRobertaModel.from_pretrained("xlm-roberta-base")
        input_ids = torch.tensor([[0, 581, 10269, 83, 99942, 136, 60742, 23, 70, 80583, 18276, 2]])
        # The dog is cute and lives in the garden house

        expected_output_shape = torch.Size((1, 12, 768))  # batch_size, sequence_length, embedding_vector_dim
        expected_output_values_last_dim = torch.tensor(
            [[-0.0101, 0.1218, -0.0803, 0.0801, 0.1327, 0.0776, -0.1215, 0.2383, 0.3338, 0.3106, 0.0300, 0.0252]]
        )
        #  xlmr = torch.hub.load('pytorch/fairseq', 'xlmr.base')
        #  xlmr.eval()
        #  expected_output_values_last_dim = xlmr.extract_features(input_ids[0])[:, :, -1]
        with torch.no_grad():
            output = model(input_ids)["last_hidden_state"].detach()
        self.assertEqual(output.shape, expected_output_shape)
        # compare the actual values for a slice of last dim
        self.assertTrue(torch.allclose(output[:, :, -1], expected_output_values_last_dim, atol=1e-3))

    @slow
    def test_xlm_roberta_large(self):
        model = XLMRobertaModel.from_pretrained("xlm-roberta-large")
        input_ids = torch.tensor([[0, 581, 10269, 83, 99942, 136, 60742, 23, 70, 80583, 18276, 2]])
        # The dog is cute and lives in the garden house

        expected_output_shape = torch.Size((1, 12, 1024))  # batch_size, sequence_length, embedding_vector_dim
        expected_output_values_last_dim = torch.tensor(
            [[-0.0699, -0.0318, 0.0705, -0.1241, 0.0999, -0.0520, 0.1004, -0.1838, -0.4704, 0.1437, 0.0821, 0.0126]]
        )
        #  xlmr = torch.hub.load('pytorch/fairseq', 'xlmr.large')
        #  xlmr.eval()
        #  expected_output_values_last_dim = xlmr.extract_features(input_ids[0])[:, :, -1]
        with torch.no_grad():
            output = model(input_ids)["last_hidden_state"].detach()
        self.assertEqual(output.shape, expected_output_shape)
        # compare the actual values for a slice of last dim
        self.assertTrue(torch.allclose(output[:, :, -1], expected_output_values_last_dim, atol=1e-3))

class XLMRobertaModelTester(object):
    def __init__(
        self,
        parent,
        batch_size=13,
        seq_length=7,
        is_training=True,
        use_input_mask=True,
        use_token_type_ids=False,
        use_labels=True,
        vocab_size=99,
        hidden_size=32,
        num_hidden_layers=2,
        num_attention_heads=4,
        intermediate_size=37,
        hidden_act="gelu",
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
        max_position_embeddings=512,
        type_vocab_size=16,
        type_sequence_label_size=2,
        initializer_range=0.02,
        num_labels=3,
        num_choices=4,
        scope=None,
    ):
        self.parent = parent
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.is_training = is_training
        self.use_input_mask = use_input_mask
        self.use_token_type_ids = use_token_type_ids
        self.use_labels = use_labels
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.type_sequence_label_size = type_sequence_label_size
        self.initializer_range = initializer_range
        self.num_labels = num_labels
        self.num_choices = num_choices
        self.scope = scope

    def prepare_config_and_inputs(self):
        input_ids = ids_tensor([self.batch_size, self.seq_length], self.vocab_size)

        input_mask = None
        if self.use_input_mask:
            input_mask = random_attention_mask([self.batch_size, self.seq_length])

        sequence_labels = None
        token_labels = None
        choice_labels = None
        if self.use_labels:
            sequence_labels = ids_tensor([self.batch_size], self.type_sequence_label_size)
            token_labels = ids_tensor([self.batch_size, self.seq_length], self.num_labels)
            choice_labels = ids_tensor([self.batch_size], self.num_choices)

        config = self.get_config()

        return config, input_ids, input_mask, sequence_labels, token_labels, choice_labels

    def get_config(self):
        return XLMRobertaConfig(
            vocab_size=self.vocab_size,
            dim=self.hidden_size,
            n_layers=self.num_hidden_layers,
            n_heads=self.num_attention_heads,
            hidden_dim=self.intermediate_size,
            hidden_act=self.hidden_act,
            dropout=self.hidden_dropout_prob,
            attention_dropout=self.attention_probs_dropout_prob,
            max_position_embeddings=self.max_position_embeddings,
            initializer_range=self.initializer_range,
        )

    def create_and_check_xlm_roberta_model(
        self, config, input_ids, input_mask, sequence_labels, token_labels, choice_labels
    ):
        model = XLMRobertaModel(config=config)
        model.to(torch_device)
        model.eval()
        result = model(input_ids, input_mask)
        result = model(input_ids)
        self.parent.assertEqual(result.last_hidden_state.shape, (self.batch_size, self.seq_length, self.hidden_size))

    def create_and_check_xlm_roberta_for_masked_lm(
        self, config, input_ids, input_mask, sequence_labels, token_labels, choice_labels
    ):
        model = XLMRobertaForMaskedLM(config=config)
        model.to(torch_device)
        model.eval()
        result = model(input_ids, attention_mask=input_mask, labels=token_labels)
        self.parent.assertEqual(result.logits.shape, (self.batch_size, self.seq_length, self.vocab_size))

    def create_and_check_xlm_roberta_for_question_answering(
        self, config, input_ids, input_mask, sequence_labels, token_labels, choice_labels
    ):
        model = XLMRobertaForQuestionAnswering(config=config)
        model.to(torch_device)
        model.eval()
        result = model(
            input_ids, attention_mask=input_mask, start_positions=sequence_labels, end_positions=sequence_labels
        )
        self.parent.assertEqual(result.start_logits.shape, (self.batch_size, self.seq_length))
        self.parent.assertEqual(result.end_logits.shape, (self.batch_size, self.seq_length))

    def create_and_check_xlm_roberta_for_sequence_classification(
        self, config, input_ids, input_mask, sequence_labels, token_labels, choice_labels
    ):
        config.num_labels = self.num_labels
        model = XLMRobertaForSequenceClassification(config)
        model.to(torch_device)
        model.eval()
        result = model(input_ids, attention_mask=input_mask, labels=sequence_labels)
        self.parent.assertEqual(result.logits.shape, (self.batch_size, self.num_labels))

    def create_and_check_xlm_roberta_for_token_classification(
        self, config, input_ids, input_mask, sequence_labels, token_labels, choice_labels
    ):
        config.num_labels = self.num_labels
        model = XLMRobertaForTokenClassification(config=config)
        model.to(torch_device)
        model.eval()

        result = model(input_ids, attention_mask=input_mask, labels=token_labels)
        self.parent.assertEqual(result.logits.shape, (self.batch_size, self.seq_length, self.num_labels))

    def create_and_check_xlm_roberta_for_multiple_choice(
        self, config, input_ids, input_mask, sequence_labels, token_labels, choice_labels
    ):
        config.num_choices = self.num_choices
        model = XLMRobertaForMultipleChoice(config=config)
        model.to(torch_device)
        model.eval()
        multiple_choice_inputs_ids = input_ids.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
        multiple_choice_input_mask = input_mask.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
        result = model(
            multiple_choice_inputs_ids,
            attention_mask=multiple_choice_input_mask,
            labels=choice_labels,
        )
        self.parent.assertEqual(result.logits.shape, (self.batch_size, self.num_choices))

    def prepare_config_and_inputs_for_common(self):
        config_and_inputs = self.prepare_config_and_inputs()
        (config, input_ids, input_mask, sequence_labels, token_labels, choice_labels) = config_and_inputs
        inputs_dict = {"input_ids": input_ids, "attention_mask": input_mask}
        return config, inputs_dict

class XLMRobertaModelTest(ModelTesterMixin, GenerationTesterMixin, PipelineTesterMixin, unittest.TestCase):
    all_model_classes = (
        (
            XLMRobertaModel,
            XLMRobertaForMaskedLM,
            XLMRobertaForMultipleChoice,
            XLMRobertaForQuestionAnswering,
            XLMRobertaForSequenceClassification,
            XLMRobertaForTokenClassification,
        )
        if is_torch_available()
        else None
    )
    pipeline_model_mapping = (
        {
            "feature-extraction": XLMRobertaModel,
            "fill-mask": XLMRobertaForMaskedLM,
            "question-answering": XLMRobertaForQuestionAnswering,
            "text-classification": XLMRobertaForSequenceClassification,
            "token-classification": XLMRobertaForTokenClassification,
            "zero-shot": XLMRobertaForSequenceClassification,
        }
        if is_torch_available()
        else {}
    )

    def setUp(self):
        self.model_tester = XLMRobertaModelTester(self)
        self.config_tester = ConfigTester(self, config_class=XLMRobertaConfig, dim=37)

    def test_config(self):
        self.config_tester.run_common_tests()

    def test_XLMRoberta_model(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_XLMRoberta_model(*config_and_inputs)

    def test_for_masked_lm(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_XLMRoberta_for_masked_lm(*config_and_inputs)

    def test_for_question_answering(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_XLMRoberta_for_question_answering(*config_and_inputs)

    def test_for_sequence_classification(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_XLMRoberta_for_sequence_classification(*config_and_inputs)

    def test_for_token_classification(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_XLMRoberta_for_token_classification(*config_and_inputs)

    def test_for_multiple_choice(self):
        config_and_inputs = self.model_tester.prepare_config_and_inputs()
        self.model_tester.create_and_check_XLMRoberta_for_multiple_choice(*config_and_inputs)

    @slow
    def test_model_from_pretrained(self):
        for model_name in XLMRoberta_PRETRAINED_MODEL_ARCHIVE_LIST[:1]:
            model = XLMRobertaModel.from_pretrained(model_name)
            self.assertIsNotNone(model)
    # Because XLMRobertaForMultipleChoice requires inputs with different shapes we need to override this test.
    @require_flash_attn
    @require_torch_accelerator
    @pytest.mark.flash_attn_test
    @slow
    def test_flash_attn_2_inference(self):
        import torch

        for model_class in self.all_model_classes:
            dummy_input = torch.LongTensor(
                [
                    [1, 2, 3, 4],
                    [1, 2, 8, 9],
                    [1, 2, 11, 12],
                    [1, 2, 13, 14],
                ]
            ).to(torch_device)
            dummy_attention_mask = torch.LongTensor(
                [
                    [0, 1, 1, 1],
                    [0, 1, 1, 1],
                    [0, 1, 1, 1],
                    [0, 1, 1, 1],
                ]
            ).to(torch_device)

            config, inputs_dict = self.model_tester.prepare_config_and_inputs_for_common()
            model = model_class(config)

            with tempfile.TemporaryDirectory() as tmpdirname:
                model.save_pretrained(tmpdirname)
                model_fa = model_class.from_pretrained(
                    tmpdirname, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2"
                )
                model_fa.to(torch_device)

                model = model_class.from_pretrained(tmpdirname, torch_dtype=torch.bfloat16)
                model.to(torch_device)

                logits = model(dummy_input, output_hidden_states=True).hidden_states[-1]
                logits_fa = model_fa(dummy_input, output_hidden_states=True).hidden_states[-1]

                self.assertTrue(torch.allclose(logits_fa, logits, atol=4e-2, rtol=4e-2))

                output_fa = model_fa(dummy_input, attention_mask=dummy_attention_mask, output_hidden_states=True)
                logits_fa = output_fa.hidden_states[-1]

                output = model(dummy_input, attention_mask=dummy_attention_mask, output_hidden_states=True)
                logits = output.hidden_states[-1]

                self.assertTrue(torch.allclose(logits_fa[1:], logits[1:], atol=4e-2, rtol=4e-2))

    # Because XLMRobertaForMultipleChoice requires inputs with different shapes we need to override this test.
    @require_flash_attn
    @require_torch_accelerator
    @pytest.mark.flash_attn_test
    @slow
    def test_flash_attn_2_inference_padding_right(self):
        import torch

        for model_class in self.all_model_classes:
            dummy_input = torch.LongTensor(
                [
                    [1, 2, 3, 4],
                    [1, 2, 8, 9],
                    [1, 2, 11, 12],
                    [1, 2, 13, 14],
                ]
            ).to(torch_device)
            dummy_attention_mask = torch.LongTensor(
                [
                    [0, 1, 1, 1],
                    [0, 1, 1, 1],
                    [0, 1, 1, 1],
                    [0, 1, 1, 1],
                ]
            ).to(torch_device)

            config, inputs_dict = self.model_tester.prepare_config_and_inputs_for_common()
            model = model_class(config)

            with tempfile.TemporaryDirectory() as tmpdirname:
                model.save_pretrained(tmpdirname)
                model_fa = model_class.from_pretrained(
                    tmpdirname, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2"
                )
                model_fa.to(torch_device)

                model = model_class.from_pretrained(
                    tmpdirname,
                    torch_dtype=torch.bfloat16,
                )
                model.to(torch_device)

                logits = model(dummy_input, output_hidden_states=True).hidden_states[-1]
                logits_fa = model_fa(dummy_input, output_hidden_states=True).hidden_states[-1]

                self.assertTrue(torch.allclose(logits_fa, logits, atol=4e-2, rtol=4e-2))

                output_fa = model_fa(dummy_input, attention_mask=dummy_attention_mask, output_hidden_states=True)
                logits_fa = output_fa.hidden_states[-1]

                output = model(dummy_input, attention_mask=dummy_attention_mask, output_hidden_states=True)
                logits = output.hidden_states[-1]

                self.assertTrue(torch.allclose(logits_fa[:-1], logits[:-1], atol=4e-2, rtol=4e-2))
