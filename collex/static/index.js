import collectionABI from "./memories_abi.js";

document.addEventListener("DOMContentLoaded", () => {
  // const web3 = new Web3(window.ethereum);
  const web3 = new Web3(Web3.givenProvider);
  const contractAddress = "0x05218d1744caf09190f72333f9167ce12d18af5c";

  document.getElementById("load_button").addEventListener("click", async () => {
    console.log("Loading NFTs...");

    const contract = new web3.eth.Contract(collectionABI, contractAddress);
    const walletAddress = document.getElementById("wallet_address").value;

    contract.defaultAccount = walletAddress;

    document.getElementById("nfts").innerHTML = "";

    let totalSupply = await contract.methods.totalSupply().call();
    console.log("Total supply:", totalSupply);

    for (let i = 0; i < 30; i++) {
      const tokenId = i;

      let tokenURI = await contract.methods.tokenURI(tokenId).call();

      tokenURI = uriHttp(tokenURI);

      const tokenMetadata = await fetch(tokenURI).then((response) =>
        response.json()
      );

      const tokenElement = document
        .getElementById("nft_template")
        .content.cloneNode(true);
      tokenElement.querySelector("h1").innerText = tokenMetadata["name"];
      tokenElement.querySelector(
        "a"
      ).href = `https://opensea.io/assets/${contractAddress}/${tokenId}`;
      const imgUri = uriHttp(tokenMetadata["image"]);
      tokenElement.querySelector("img").src = imgUri;
      tokenElement.querySelector("img").alt = tokenMetadata["description"];

      document.getElementById("nfts").append(tokenElement);
    }

    console.log("Done.");
  });
});
function uriHttp(tokenMetadataURI) {
  if (tokenMetadataURI.startsWith("ipfs://")) {
    tokenMetadataURI = `https://ipfs.io/ipfs/${
      tokenMetadataURI.split("ipfs://")[1]
    }`;
  }
  return tokenMetadataURI;
}
