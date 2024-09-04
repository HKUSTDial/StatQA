# When you use NVIDIA RTX 4000 Series GPUs for distributed training, you may encounter some specific hardware limitations, 
# such as not supporting faster communication via P2P (peer-to-peer) or IB (InfiniBand). 
# In this case, you may see a NotImplementedError prompting you to disable these features.
# You can solve this problem by setting environment variables
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

# Please set your available GPUs for training
wait
CUDA_VISIBLE_DEVICES=0,1,2,3 llamafactory-cli train ../Finetuning/Config/llama2_7b_lora_sft.yaml
echo "-----------------------------------------------------------"
echo " [i] SFT: fine-tuning for LLaMA-2-7b is finished!"
echo "-----------------------------------------------------------"

wait
CUDA_VISIBLE_DEVICES=0,1,2,3 llamafactory-cli train ../Finetuning/Config/llama3_8b_lora_sft.yaml
echo "-----------------------------------------------------------"
echo " [i] SFT: fine-tuning for LLaMA-3-8b is finished!"
echo "-----------------------------------------------------------"

wait
CUDA_VISIBLE_DEVICES=0,1,2,3 llamafactory-cli train ../Finetuning/Config/llama3_8b_instruct_lora_sft.yaml
echo "-----------------------------------------------------------"
echo " [i] SFT: fine-tuning for LLaMA-3-8b-instruct is finished!"
echo "-----------------------------------------------------------"