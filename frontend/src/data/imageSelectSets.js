import { agents } from './hashcodes.js';
import { weapons } from './hashcodes.js';
import { armors } from './hashcodes.js';
import { maps } from './hashcodes.js';


export const agentOptions = Object.entries(agents).map(([label, hashcode]) => ({
    label,
    hashcode,
    image: `/images/valorant/agents/${hashcode}.png`,
}));

export const weaponOptions = Object.entries(weapons).map(([label, hashcode]) => ({
    label,
    hashcode,
    image: `/images/valorant/weapons/${hashcode}_killstream.png`,
}));

export const armorOptions = Object.entries(armors).map(([label, hashcode]) => ({
    label,
    hashcode,
    image: `/images/valorant/armors/${hashcode}.png`,
}));

export const mapOptions = Object.entries(maps).map(([label, hashcode]) => ({
    label,
    hashcode,
    image: `/images/valorant/maps/${hashcode}_listview.png`,
}));