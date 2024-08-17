#version 330 core

uniform int u_metaballCount;
uniform vec3[500] u_metaballs;
uniform sampler2D u_imageTexture;
uniform vec2 u_texSize;

in vec2 fragmentTexCoord;

out vec4 color;

vec2 pixel = 1.0 / u_texSize;

void main() {
    color = vec4(0.0, 0.0, 0.0, 1.0);
    vec2 coord = vec2(fragmentTexCoord / pixel);
    coord.y = u_texSize.y - coord.y;
    float sum = 0.0;
    for (int i = 0; i < u_metaballCount; i++) {
        vec2 metaball = u_metaballs[i].xy;
        sum += pow(u_metaballs[i].z, 2) / (pow(coord.x - metaball.x, 2) + pow(coord.y - metaball.y, 2));
    }
    if (sum > 1.0) {
        color = vec4(1.0, 1.0, 1.0, 1.0);
    }
}
