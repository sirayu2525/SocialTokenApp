import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("SocialTokenModule", (m) => {
    const socialToken = m.contract("SocialToken", ["SocialToken", "SCT"]);

    return { socialToken };
});
